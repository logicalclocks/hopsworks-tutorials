package com.hopsworks.tutorials.beam.clickstreampipe.options;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.PipelineOptions;

@Experimental
public interface RetailPipelineTransactionsOptions extends PipelineOptions {
  
  @Default.String("subscriptions/global-transaction-topic")
  String getTransactionsPubSubSubscription();
  
  void setTransactionsPubSubSubscription(String transactionsOutput);
  
  @Default.String("Retail_Store.raw_transactions_data")
  String getTransactionsBigQueryRawTable();
  
  void setTransactionsBigQueryRawTable(String transactionsBigQueryRawTable);
  
  @Default.String("Retail_Store.clean_transaction_data")
  String getTransactionsBigQueryCleanTable();
  
  void setTransactionsBigQueryCleanTable(String transactionsBigQueryCleanTable);
}
