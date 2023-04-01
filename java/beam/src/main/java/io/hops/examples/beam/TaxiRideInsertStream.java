package io.hops.examples.beam;

import com.logicalclocks.hsfs.beam.FeatureStore;
import com.logicalclocks.hsfs.beam.HopsworksConnection;
import com.logicalclocks.hsfs.beam.StreamFeatureGroup;

import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions;
import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubIO;
import org.apache.beam.sdk.options.Description;

import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.schemas.Schema;
import org.apache.beam.sdk.schemas.Schema.Field;
import org.apache.beam.sdk.schemas.Schema.FieldType;

import org.apache.beam.sdk.transforms.JsonToRow;

public class TaxiRideInsertStream {
  
  public interface WriteHopsWorksOptions extends DataflowPipelineOptions {
    
    @Description("Hopsworks cluster host")
    String getHopsworksHost();
    void setHopsworksHost(String value);
    
    @Description("API key to authenticate with Hopsworks")
    String getHopsworksApi();
    void setHopsworksApi(String value);
  
    @Description("Name of the Hopsworks project to connect to")
    String getHopsworksProject();
    void setHopsworksProject(String value);
  
    @Description("Name of the Feature group to write to")
    String getFeatureGroupName();
    void setFeatureGroupName(String value);
  
    @Description("Version of the Feature group to write to")
    Integer getFeatureGroupVersion();
    void setFeatureGroupVersion(Integer value);
    
    @Description("Source topic to subscribe to")
    String getInputTopic();
    void setInputTopic(String value);
  }
  
  
  public static void main(String[] args) throws Exception {
  
    WriteHopsWorksOptions options = PipelineOptionsFactory.fromArgs(args).withValidation().as(WriteHopsWorksOptions.class);
  
    FeatureStore fs = HopsworksConnection.builder()
      
      .host(options.getHopsworksHost())
      .project(options.getHopsworksProject())
      .apiKeyValue(options.getHopsworksApi())
      .hostnameVerification(false)
      .build()
      .getFeatureStore();
    StreamFeatureGroup featureGroup = fs.getStreamFeatureGroup(options.getFeatureGroupName(),
      options.getFeatureGroupVersion());
  
    Pipeline p = Pipeline.create(options);
  
    Schema schema =
      Schema.of(
        Field.nullable("ride_id", FieldType.STRING),
        Field.nullable("ride_status", FieldType.STRING),
        Field.nullable("point_idx", FieldType.INT32),
        Field.nullable("longitude", FieldType.DOUBLE),
        Field.nullable("latitude", FieldType.DOUBLE),
        Field.nullable("meter_reading", FieldType.DOUBLE),
        Field.nullable("meter_increment", FieldType.DOUBLE),
        Field.nullable("passenger_count", FieldType.DOUBLE)
      );

    p
      .apply("ReadFromPubSub", PubsubIO.readStrings().fromTopic(options.getInputTopic()))
      .apply("Parse JSON to Beam Rows", JsonToRow.withSchema(schema))
      .apply("insert to stream feature group", featureGroup.insertStream());
    
    p.run().waitUntilFinish();
  }
}
