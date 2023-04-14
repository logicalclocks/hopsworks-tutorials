package com.hopsworks.tutorials.beam.clickstreampipe.options;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.Description;
import org.apache.beam.sdk.options.PipelineOptions;

@Experimental
public interface RetailPipelineReportingOptions extends PipelineOptions {
  
  @Description("Bluh blih.")
  @Default.String("/topics/global-stock-level-topic")
  String getAggregateStockPubSubOutputTopic();
  
  void setAggregateStockPubSubOutputTopic(String aggregateStockPubSubOutputTopic);
}
