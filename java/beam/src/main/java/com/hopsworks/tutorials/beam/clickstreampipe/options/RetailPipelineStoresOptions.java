package com.hopsworks.tutorials.beam.clickstreampipe.options;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.Description;
import org.apache.beam.sdk.options.PipelineOptions;

@Experimental
public interface RetailPipelineStoresOptions extends PipelineOptions {
  
  @Description("Store Location BigQuery TableReference")
  @Default.String("Retail_Store.Store_Locations")
  String getStoreLocationBigQueryTableRef();
  
  void setStoreLocationBigQueryTableRef(String storeLocationTableRef);
}
