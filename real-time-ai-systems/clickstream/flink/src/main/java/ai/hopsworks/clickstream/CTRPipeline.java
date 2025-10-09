package ai.hopsworks.clickstream;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.logicalclocks.hsfs.flink.FeatureStore;
import com.logicalclocks.hsfs.flink.HopsworksConnection;
import com.logicalclocks.hsfs.flink.StreamFeatureGroup;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.AbstractDeserializationSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.io.IOException;
import java.time.Duration;

public class CTRPipeline {

    private static final String KAFKA_TOPIC = "clickstream_events";
    private static final String FEATURE_GROUP_NAME = "ctr_5min_flink";
    private static final int FEATURE_GROUP_VERSION = 1;

    public static void main(String[] args) throws Exception {
        // Setup Flink environment
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);

        // Connect to Hopsworks
        HopsworksConnection connection = HopsworksConnection.builder()
            .host(System.getenv("HOPSWORKS_HOST"))
            .port(Integer.parseInt(System.getenv("HOPSWORKS_PORT")))
            .project(System.getenv("HOPSWORKS_PROJECT"))
            .apiKeyValue(System.getenv("HOPSWORKS_API_KEY"))
            .build();

        FeatureStore fs = connection.getFeatureStore();

        // Get Kafka configuration from Hopsworks
        String kafkaBootstrapServers = System.getenv("KAFKA_BOOTSTRAP_SERVERS");

        // Create Kafka source
        KafkaSource<ClickEvent> source = KafkaSource.<ClickEvent>builder()
            .setBootstrapServers(kafkaBootstrapServers)
            .setTopics(KAFKA_TOPIC)
            .setGroupId("ctr-flink-consumer")
            .setStartingOffsets(OffsetsInitializer.earliest())
            .setValueOnlyDeserializer(new ClickEventDeserializer())
            .build();

        // Create streaming pipeline
        DataStream<ClickEvent> events = env.fromSource(
            source,
            WatermarkStrategy.<ClickEvent>forBoundedOutOfOrderness(Duration.ofSeconds(10))
                .withTimestampAssigner((event, timestamp) -> event.getTimestamp()),
            "Kafka Source"
        );

        // Calculate CTR in 5-minute tumbling windows
        DataStream<CTRAgg> ctrStream = events
            .keyBy(ClickEvent::getUserId)
            .window(TumblingEventTimeWindows.of(Time.minutes(5)))
            .aggregate(new CTRAccumulator(), new CTRWindowFunction());

        // Write to Hopsworks Feature Store
        StreamFeatureGroup featureGroup = fs.getStreamFeatureGroup(FEATURE_GROUP_NAME, FEATURE_GROUP_VERSION);
        featureGroup.insertStream(ctrStream);

        // Execute pipeline
        env.execute("CTR Streaming Pipeline");
    }

    // Custom deserializer for ClickEvent
    public static class ClickEventDeserializer extends AbstractDeserializationSchema<ClickEvent> {
        private transient ObjectMapper mapper;

        @Override
        public void open(InitializationContext context) {
            mapper = new ObjectMapper();
        }

        @Override
        public ClickEvent deserialize(byte[] message) throws IOException {
            return mapper.readValue(message, ClickEvent.class);
        }

        @Override
        public boolean isEndOfStream(ClickEvent nextElement) {
            return false;
        }
    }
}