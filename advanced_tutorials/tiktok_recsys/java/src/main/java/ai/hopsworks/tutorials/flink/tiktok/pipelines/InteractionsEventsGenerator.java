package ai.hopsworks.tutorials.flink.tiktok.pipelines;

import ai.hopsworks.tutorials.flink.tiktok.features.SourceInteractions;
import ai.hopsworks.tutorials.flink.tiktok.simulators.InteractionsGenerator;
import ai.hopsworks.tutorials.flink.tiktok.utils.InteractionsEventKafkaSync;
import ai.hopsworks.tutorials.flink.tiktok.utils.TikTokInteractions;
import ai.hopsworks.tutorials.flink.tiktok.utils.Utils;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.connector.source.util.ratelimit.RateLimiterStrategy;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.datagen.source.DataGeneratorSource;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Properties;

public class InteractionsEventsGenerator {
    Utils utils = new Utils();
    public void run(String topicName, Long recordsPerSecond, Integer parallelism) throws Exception {

        // Define time for start
        Instant now = Instant.now();
        // Subtract 2 weeks from the current instant
        Instant startTime = now.minus(7, ChronoUnit.DAYS);

        // set up streaming execution environment
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(parallelism);

        DataGeneratorSource<TikTokInteractions> generatorSource =
                new DataGeneratorSource<>(
                        new InteractionsGenerator(recordsPerSecond, startTime),
                        Long.MAX_VALUE,
                        RateLimiterStrategy.perSecond(recordsPerSecond),
                        TypeInformation.of(TikTokInteractions.class));

        DataStream<SourceInteractions> simEvents =
                env.fromSource(generatorSource,
                                WatermarkStrategy.noWatermarks(),
                                "Generator Source")
                        //.setParallelism(parallelism)
                        .rescale()
                        .rebalance()
                        .keyBy(TikTokInteractions::getUserId)
                        .map(new MapFunction<TikTokInteractions, SourceInteractions>() {
                            @Override
                            public SourceInteractions map(TikTokInteractions tikTokInteractions) throws Exception {
                                SourceInteractions sourceInteractions = new SourceInteractions();
                                sourceInteractions.setId(tikTokInteractions.getInteractionId());
                                sourceInteractions.setUserId(tikTokInteractions.getUserId());
                                sourceInteractions.setVideoId(tikTokInteractions.getVideoId());
                                sourceInteractions.setCategoryId(tikTokInteractions.getCategoryId());
                                sourceInteractions.setInteractionType(tikTokInteractions.getInteractionType());
                                sourceInteractions.setInteractionDate(tikTokInteractions.getInteractionDate());
                                sourceInteractions.setInteractionMonth(tikTokInteractions.getInteractionMonth());
                                sourceInteractions.setWatchTime(tikTokInteractions.getWatchTime());
                                return sourceInteractions;
                            }
                        });

        Properties kafkaConfig = utils.getKafkaProperties(topicName);

        KafkaSink<SourceInteractions> sink = KafkaSink.<SourceInteractions>builder()
                .setKafkaProducerConfig(kafkaConfig)
                .setBootstrapServers(kafkaConfig.getProperty("bootstrap.servers"))
                .setRecordSerializer(new InteractionsEventKafkaSync(topicName))
                .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
                .build();

        simEvents.sinkTo(sink);

        env.execute();
    }
    public static void main(String[] args) throws Exception {

        Options options = new Options();

        options.addOption(Option.builder("topicName")
                .argName("topicName")
                .required(true)
                .hasArg()
                .build());

        options.addOption(Option.builder("recordsPerSecond")
                .argName("recordsPerSecond")
                .required(true)
                .hasArg()
                .build());

        options.addOption(Option.builder("parallelism")
                .argName("parallelism")
                .required(true)
                .hasArg()
                .build());

        CommandLineParser parser = new DefaultParser();
        CommandLine commandLine = parser.parse(options, args);

        String topicName = commandLine.getOptionValue("topicName");
        Long recordsPerSecond = Long.parseLong(commandLine.getOptionValue("recordsPerSecond"));
        Integer parallelism = Integer.parseInt(commandLine.getOptionValue("parallelism"));

        InteractionsEventsGenerator interactionsEventsProducer = new InteractionsEventsGenerator();
        interactionsEventsProducer.run(topicName, recordsPerSecond, parallelism);
    }
}
