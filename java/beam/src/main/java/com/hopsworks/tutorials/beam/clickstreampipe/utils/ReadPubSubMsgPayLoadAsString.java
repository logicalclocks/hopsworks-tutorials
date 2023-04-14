package com.hopsworks.tutorials.beam.clickstreampipe.utils;

import javax.annotation.Nullable;

import com.hopsworks.tutorials.beam.clickstreampipe.options.RetailPipelineOptions;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubIO;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.values.PBegin;
import org.apache.beam.sdk.values.PCollection;

/** Wrapper to ensure that timestamp attribute has been set for PubSub. */
@Experimental
public class ReadPubSubMsgPayLoadAsString extends PTransform<PBegin, PCollection<String>> {
  
  private String pubsubTopic;
  
  public ReadPubSubMsgPayLoadAsString(String pubsubTopic) {
    this.pubsubTopic = pubsubTopic;
  }
  
  public ReadPubSubMsgPayLoadAsString(@Nullable String name, String pubsubTopic) {
    super(name);
    this.pubsubTopic = pubsubTopic;
  }
  
  @Override
  public PCollection<String> expand(PBegin input) {
    /**
     * **********************************************************************************************
     * Read our events from PubSub topics. The values are sent as JSON.
     * **********************************************************************************************
     */
    PCollection<String> pubSubMessages =
      input.apply(
        "ReadStream",
        PubsubIO.readStrings()
          .fromSubscription(pubsubTopic)
          .withTimestampAttribute("TIMESTAMP"));
    
    /** Output raw values if in debug mode. */
    if (input.getPipeline().getOptions().as(RetailPipelineOptions.class).getDebugMode()) {
      pubSubMessages.apply(
        ParDo.of(
          new DoFn<String, Void>() {
            @ProcessElement
            public void process(ProcessContext pc) {
              System.out.println(pc.element());
            }
          }));
    }
    return pubSubMessages;
  }
}