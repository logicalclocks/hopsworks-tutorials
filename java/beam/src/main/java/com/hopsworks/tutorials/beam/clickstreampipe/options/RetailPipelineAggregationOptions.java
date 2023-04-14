package com.hopsworks.tutorials.beam.clickstreampipe.options;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.io.gcp.bigquery.BigQueryOptions;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.Description;

@Experimental
public interface RetailPipelineAggregationOptions extends BigQueryOptions {
  
  @Default.String("aggregate-tables")
  String getAggregateBigTableInstance();
  
  void setAggregateBigTableInstance(String aggregateBigTableInstance);
  
  @Default.String("Retail_Store_Aggregations")
  String getAggregateBigQueryTable();
  
  void setAggregateBigQueryTable(String aggregateBigQueryTable);
  
  @Description("The fixed window period which aggregations are computed over")
  @Default.Integer(5)
  Integer getAggregationDefaultSec();
  
  void setAggregationDefaultSec(Integer aggregationDefaultSec);
}
