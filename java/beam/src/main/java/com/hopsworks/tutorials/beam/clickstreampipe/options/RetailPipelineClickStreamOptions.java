package com.hopsworks.tutorials.beam.clickstreampipe.options;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubOptions;
import org.apache.beam.sdk.options.Default;

@Experimental
public interface RetailPipelineClickStreamOptions extends PubsubOptions {
  
  @Default.String("subscriptions/clickstreampipe-inbound-sub")
  String getClickStreamPubSubSubscription();
  void setClickStreamPubSubSubscription(String clickStreamOutput);
  
  @Default.String("Retail_Store.sessionized_clickstream")
  String getClickStreamSessionizedTable();
  void setClickStreamSessionizedTable(String clickStreamSessionizedTable);
}
