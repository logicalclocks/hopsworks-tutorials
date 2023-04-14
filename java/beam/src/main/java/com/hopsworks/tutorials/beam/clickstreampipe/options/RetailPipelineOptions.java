package com.hopsworks.tutorials.beam.clickstreampipe.options;

import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.options.Default;

@Experimental
public interface RetailPipelineOptions
  extends DataflowPipelineOptions,
  RetailPipelineAggregationOptions,
  RetailPipelineClickStreamOptions,
  RetailPipelineInventoryOptions,
  RetailPipelineTransactionsOptions,
  RetailPipelineStoresOptions,
  RetailPipelineReportingOptions {
  
  @Default.Boolean(false)
  Boolean getDebugMode();
  
  void setDebugMode(Boolean debugMode);
  
  @Default.Boolean(false)
  Boolean getTestModeEnabled();
  
  void setTestModeEnabled(Boolean testModeEnabled);
}
