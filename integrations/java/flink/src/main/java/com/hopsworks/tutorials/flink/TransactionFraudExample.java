package com.hopsworks.tutorials.flink;

import com.hopsworks.tutorials.flink.fraud.TransactionCountAggregate;
import com.hopsworks.tutorials.flink.fraud.TransactionsDeserializer;
import com.hopsworks.tutorials.flink.utils.Utils;
import com.logicalclocks.hsfs.flink.FeatureStore;
import com.logicalclocks.hsfs.flink.HopsworksConnection;
import com.logicalclocks.hsfs.flink.StreamFeatureGroup;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.time.Duration;
import java.util.Properties;

public class TransactionFraudExample {
  
  private Utils customUtils = new Utils();
  
  public void run(String featureGroupName, Integer featureGroupVersion, String sourceTopic, Integer windowLength)
    throws Exception {
    
    Duration maxOutOfOrderness = Duration.ofSeconds(60);
    
    // define flink env
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.getConfig().enableObjectReuse();
    env.enableCheckpointing(30000);
    
    //get feature store handle
    FeatureStore fs = HopsworksConnection.builder().build().getFeatureStore();
    
    // get or create stream feature group
    StreamFeatureGroup featureGroup = fs.getStreamFeatureGroup(featureGroupName, featureGroupVersion);
    
    Properties kafkaProperties = customUtils.getKafkaProperties();
    
    // define transaction source
    KafkaSource<SourceTransaction> transactionSource = KafkaSource.<SourceTransaction>builder()
      .setProperties(kafkaProperties)
      .setTopics(sourceTopic)
      .setStartingOffsets(OffsetsInitializer.earliest())
      .setDeserializer(KafkaRecordDeserializationSchema.of(new TransactionsDeserializer()))
      .build();
    
    // define watermark strategy
    WatermarkStrategy<SourceTransaction> customWatermark = WatermarkStrategy
      .<SourceTransaction>forBoundedOutOfOrderness(maxOutOfOrderness)
      .withTimestampAssigner((event, timestamp) -> event.getDatetime());
    
    // aggregate stream and return DataStream<TransactionAgg>
    DataStream<TransactionAgg> aggregationStream =
      env.fromSource(transactionSource, customWatermark, "Transaction Kafka Source")
      .rescale()
      .rebalance()
      .keyBy(r -> r.getCcNum())
      .window(SlidingEventTimeWindows.of(Time.minutes(windowLength), Time.minutes(1)))
      .aggregate(new TransactionCountAggregate());
    
    // insert stream
    featureGroup.insertStream(aggregationStream);

    env.execute("Feature pipeline for Feature Group " + featureGroupName + " with version "
      + featureGroupVersion);
  }
  
  public static void main(String[] args) throws Exception {
    Options options = new Options();
    
    options.addOption(Option.builder("featureGroupName")
      .argName("featureGroupName")
      .required(true)
      .hasArg()
      .build());
    
    options.addOption(Option.builder("featureGroupVersion")
      .argName("featureGroupVersion")
      .required(true)
      .hasArg()
      .build());
    
    options.addOption(Option.builder("sourceTopic")
      .argName("sourceTopic")
      .required(true)
      .hasArg()
      .build());
    
    options.addOption(Option.builder("windowLength")
      .argName("windowLength")
      .required(true)
      .hasArg()
      .build());
    
    CommandLineParser parser = new DefaultParser();
    CommandLine commandLine = parser.parse(options, args);
    
    String featureGroupName = commandLine.getOptionValue("featureGroupName");
    Integer featureGroupVersion = Integer.parseInt(commandLine.getOptionValue("featureGroupVersion"));
    String sourceTopic = commandLine.getOptionValue("sourceTopic");
    Integer windowLength = Integer.parseInt(commandLine.getOptionValue("windowLength"));
    
    TransactionFraudExample transactionFraudExample = new TransactionFraudExample();
    transactionFraudExample.run(featureGroupName, featureGroupVersion, sourceTopic, windowLength);
  }
}