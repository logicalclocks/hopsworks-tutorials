package ai.hopsworks.tutorials.flink.tiktok.utils;

import ai.hopsworks.tutorials.flink.tiktok.features.SourceInteractions;
import lombok.SneakyThrows;
import org.apache.avro.io.BinaryDecoder;
import org.apache.avro.io.DatumReader;
import org.apache.avro.io.DecoderFactory;
import org.apache.avro.specific.SpecificDatumReader;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.streaming.connectors.kafka.KafkaDeserializationSchema;
import org.apache.flink.util.Collector;
import org.apache.kafka.clients.consumer.ConsumerRecord;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.time.Instant;

public class InteractionsEventKafkaSource implements KafkaDeserializationSchema<TikTokInteractions>,
        KafkaRecordDeserializationSchema<TikTokInteractions> {

    @Override
    public void open(DeserializationSchema.InitializationContext context) throws Exception {
        KafkaRecordDeserializationSchema.super.open(context);
    }

    @Override
    public boolean isEndOfStream(TikTokInteractions sourceInteractions) {
        return false;
    }

    @Override
    public TikTokInteractions deserialize(ConsumerRecord<byte[], byte[]> consumerRecord) throws Exception {
        byte[] messageKey = consumerRecord.key();
        byte[] message = consumerRecord.value();
        long offset = consumerRecord.offset();
        long timestamp = consumerRecord.timestamp();

        SourceInteractions sourceInteractions = new SourceInteractions();
        ByteArrayInputStream in = new ByteArrayInputStream(message);
        DatumReader<SourceInteractions> userDatumReader = new SpecificDatumReader<>(sourceInteractions.getSchema());
        BinaryDecoder decoder = DecoderFactory.get().directBinaryDecoder(in, null);
        sourceInteractions = userDatumReader.read(null, decoder);

        TikTokInteractions interactions = getTikTokInteractions(sourceInteractions);

        return interactions;
    }

    private static TikTokInteractions getTikTokInteractions(SourceInteractions sourceInteractions) {
        TikTokInteractions interactions = new TikTokInteractions();
        interactions.setInteractionId(sourceInteractions.getId());
        interactions.setUserId(sourceInteractions.getUserId());
        interactions.setVideoId(sourceInteractions.getVideoId());
        interactions.setCategoryId(sourceInteractions.getCategoryId());
        interactions.setInteractionType(String.valueOf(sourceInteractions.getInteractionType()));
        interactions.setInteractionDate(sourceInteractions.getInteractionDate());
        interactions.setInteractionMonth(String.valueOf(sourceInteractions.getInteractionMonth()));
        interactions.setWatchTime(sourceInteractions.getWatchTime());
        return interactions;
    }

    @SneakyThrows
    @Override
    public void deserialize(ConsumerRecord<byte[], byte[]> consumerRecord, Collector<TikTokInteractions> collector)
            throws IOException {
        long deserializeStart = Instant.now().toEpochMilli();
        TikTokInteractions sourceInteractions = deserialize(consumerRecord);
        sourceInteractions.setProcessStart(deserializeStart);
        collector.collect(sourceInteractions);
    }

    @Override
    public TypeInformation<TikTokInteractions> getProducedType() {
        return TypeInformation.of(TikTokInteractions.class);
    }
}
