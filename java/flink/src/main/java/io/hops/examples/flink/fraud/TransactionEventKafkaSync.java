package io.hops.examples.flink.fraud;

import io.hops.examples.flink.examples.SourceTransaction;
import lombok.SneakyThrows;
import org.apache.avro.io.BinaryEncoder;
import org.apache.avro.io.DatumWriter;
import org.apache.avro.io.EncoderFactory;
import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.flink.api.common.serialization.SerializationSchema;

import java.io.ByteArrayOutputStream;

public class TransactionEventKafkaSync implements SerializationSchema<SourceTransaction> {
  @SneakyThrows
  @Override
  public byte[] serialize(SourceTransaction transactionEvent) {
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    BinaryEncoder encoder = EncoderFactory.get().binaryEncoder(out, null);
    DatumWriter<SourceTransaction> dataFileWriter = new SpecificDatumWriter<>(transactionEvent.getSchema());
    dataFileWriter.write(transactionEvent, encoder);
    encoder.flush();
    return out.toByteArray();
  }
}
