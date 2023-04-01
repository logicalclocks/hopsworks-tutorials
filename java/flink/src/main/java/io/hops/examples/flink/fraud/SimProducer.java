package io.hops.examples.flink.fraud;

import io.hops.examples.flink.examples.SourceTransaction;
import io.hops.examples.flink.utils.Utils;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;

public class SimProducer {
  private static final Logger LOG = LoggerFactory.getLogger(SimProducer.class);

  Utils utils = new Utils();
  public void run(String topicName, Integer batchSize) throws Exception {
    
    // set up streaming execution environment
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.setParallelism(1);
  
    DataStream<SourceTransaction> simEvens =
      env.addSource(new TransactionEventSimulator(batchSize)).keyBy(r -> r.getCcNum());
    Properties kafkaCinfig = utils.getKafkaProperties(topicName);
    KafkaSink<SourceTransaction> sink = KafkaSink.<SourceTransaction>builder()
      .setKafkaProducerConfig(kafkaCinfig)
      .setBootstrapServers(kafkaCinfig.getProperty("bootstrap.servers"))
      .setRecordSerializer(KafkaRecordSerializationSchema.builder()
        .setTopic(topicName)
        .setValueSerializationSchema(new TransactionEventKafkaSync())
        .build()
      )
      .setDeliverGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
      .build();
    
    simEvens.sinkTo(sink);
    
    env.execute();
  }
  
  public static void main(String[] args) throws Exception {
    
    Options options = new Options();
    
    options.addOption(Option.builder("topicName")
      .argName("topicName")
      .required(true)
      .hasArg()
      .build());
    
    options.addOption(Option.builder("batchSize")
      .argName("batchSize")
      .required(true)
      .hasArg()
      .build());
    
    CommandLineParser parser = new DefaultParser();
    CommandLine commandLine = parser.parse(options, args);
    
    String topicName = commandLine.getOptionValue("topicName");
    Integer batchSize = Integer.parseInt(commandLine.getOptionValue("batchSize"));
    
    SimProducer simProducer = new SimProducer();
    simProducer.run(topicName, batchSize);
  }
}
