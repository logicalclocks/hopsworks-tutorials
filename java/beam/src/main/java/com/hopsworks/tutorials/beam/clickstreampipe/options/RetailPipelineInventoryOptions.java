package com.hopsworks.tutorials.beam.clickstreampipe.options;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.PipelineOptions;

@Experimental
public interface RetailPipelineInventoryOptions extends PipelineOptions {
  
  @Default.String("subscriptions/global-inventory-topic")
  String getInventoryPubSubSubscriptions();
  
  void setInventoryPubSubSubscriptions(String inventoryOutput);
  
  @Default.String("Retail_Store.raw_inventory_data")
  String getInventoryBigQueryRawTable();
  
  void setInventoryBigQueryRawTable(String clickStreamBigQueryRawTable);
  
  @Default.String("Retail_Store.clean_inventory_data")
  String getInventoryBigQueryCleanTable();
  
  void setInventoryBigQueryCleanTable(String clickStreamBigQueryRawTable);
}
