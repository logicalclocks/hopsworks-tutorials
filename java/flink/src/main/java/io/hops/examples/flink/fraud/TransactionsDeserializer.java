package io.hops.examples.flink.fraud;

import io.hops.examples.flink.examples.SourceTransaction;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.formats.avro.AvroDeserializationSchema;
import org.apache.flink.streaming.connectors.kafka.KafkaDeserializationSchema;
import org.apache.kafka.clients.consumer.ConsumerRecord;

public class TransactionsDeserializer implements KafkaDeserializationSchema<SourceTransaction> {
  
  @Override
  public boolean isEndOfStream(SourceTransaction sourceTransaction) {
    return false;
  }
  
  @Override
  public SourceTransaction deserialize(ConsumerRecord<byte[], byte[]> consumerRecord) throws Exception {
    byte[] messageKey = consumerRecord.key();
    byte[] message = consumerRecord.value();
    long offset = consumerRecord.offset();
    long timestamp = consumerRecord.timestamp();
    DeserializationSchema<SourceTransaction> deserializer =
      AvroDeserializationSchema.forSpecific(SourceTransaction.class);
    return deserializer.deserialize(message);
  }
  
  @Override
  public TypeInformation<SourceTransaction> getProducedType() {
    return TypeInformation.of(SourceTransaction.class);
  }
}
