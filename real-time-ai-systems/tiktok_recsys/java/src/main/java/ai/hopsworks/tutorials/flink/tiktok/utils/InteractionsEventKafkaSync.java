package ai.hopsworks.tutorials.flink.tiktok.utils;

import ai.hopsworks.tutorials.flink.tiktok.features.SourceInteractions;
import lombok.SneakyThrows;
import org.apache.avro.io.BinaryEncoder;
import org.apache.avro.io.DatumWriter;
import org.apache.avro.io.EncoderFactory;
import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.flink.api.common.serialization.SerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.runtime.metrics.DescriptiveStatisticsHistogram;
import org.apache.kafka.clients.producer.ProducerRecord;

import javax.annotation.Nullable;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.time.Instant;

public class InteractionsEventKafkaSync implements KafkaRecordSerializationSchema<SourceInteractions> {


    private static final int EVENT_TIME_LAG_WINDOW_SIZE = 10_000;

    private transient DescriptiveStatisticsHistogram eventTimeLag;

    private final String topic;

    public InteractionsEventKafkaSync(String topic) {
        this.topic = topic;
    }

    @SneakyThrows
    public byte[] serializeValue(SourceInteractions interactionEvent) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        BinaryEncoder encoder = EncoderFactory.get().binaryEncoder(out, null);
        DatumWriter<SourceInteractions> dataFileWriter = new SpecificDatumWriter<>(SourceInteractions.class);
        dataFileWriter.write(interactionEvent, encoder);
        encoder.flush();
        return out.toByteArray();
    }

    public byte[] serializeKey(SourceInteractions interactionEvent) {
        return String.valueOf(interactionEvent.getUserId()).getBytes(StandardCharsets.UTF_8);
    }

    @Override
    public void open(SerializationSchema.InitializationContext context, KafkaSinkContext sinkContext) throws Exception {
        KafkaRecordSerializationSchema.super.open(context, sinkContext);
        eventTimeLag =
                context
                        .getMetricGroup()
                        .histogram(
                                "interactionsEventKafkaSyncLag",
                                new DescriptiveStatisticsHistogram(EVENT_TIME_LAG_WINDOW_SIZE));
    }
    @Nullable
    @Override
    public ProducerRecord<byte[], byte[]> serialize(SourceInteractions sourceInteractions,
                                                    KafkaSinkContext kafkaSinkContext, Long timestamp) {
        byte[] key = this.serializeKey(sourceInteractions);
        byte[] value = this.serializeValue(sourceInteractions);
        eventTimeLag.update(Instant.now().toEpochMilli() - sourceInteractions.getInteractionDate());

        return new ProducerRecord<>(topic, null, timestamp, key, value);
    }

}