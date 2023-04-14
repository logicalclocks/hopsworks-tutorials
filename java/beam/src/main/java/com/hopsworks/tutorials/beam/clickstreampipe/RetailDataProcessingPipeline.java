package com.hopsworks.tutorials.beam.clickstreampipe;

import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.CountGlobalStockFromTransaction;
import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.CountGlobalStockUpdatePerProduct;
import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.CountIncomingStockPerProductLocation;
import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.StockAggregation;
import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.TransactionPerProductAndLocation;
import com.hopsworks.tutorials.beam.clickstreampipe.options.RetailPipelineOptions;
import com.hopsworks.tutorials.beam.clickstreampipe.processing.ClickstreamProcessing;
import com.hopsworks.tutorials.beam.clickstreampipe.processing.StockProcessing;
import com.hopsworks.tutorials.beam.clickstreampipe.processing.TransactionProcessing;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Stock;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Transaction;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.ReadPubSubMsgPayLoadAsString;

import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubIO;
import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.transforms.Flatten;
import org.apache.beam.sdk.transforms.MapElements;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.PCollectionList;
import org.apache.beam.sdk.values.TypeDescriptors;

import org.joda.time.Duration;

/**
 * Primary pipeline using {@link ClickstreamProcessing}, {@link TransactionProcessing}, {@link
 * StockProcessing}.
 */
@Experimental
public class RetailDataProcessingPipeline {
  
  public void startRetailPipeline(Pipeline p) throws Exception {
    
    RetailPipelineOptions options = p.getOptions().as(RetailPipelineOptions.class);
    
    /**
     * **********************************************************************************************
     * Process Clickstream
     * **********************************************************************************************
     */
    PCollection<String> clickStreamJSONMessages =
      p.apply(
        "ReadClickStream",
        PubsubIO.readStrings()
          .fromSubscription(options.getClickStreamPubSubSubscription())
          .withTimestampAttribute("TIMESTAMP"));
    
    clickStreamJSONMessages.apply(new ClickstreamProcessing());
    
    /**
     * **********************************************************************************************
     * Process Transactions
     * **********************************************************************************************
     */
    PCollection<String> transactionsJSON =
        p.apply(
          "ReadTransactionStream",
          new ReadPubSubMsgPayLoadAsString(options.getTransactionsPubSubSubscription()));
    
    PCollection<Transaction.TransactionEvent> transactionWithStoreLoc =
      transactionsJSON.apply(new TransactionProcessing());
    
    /**
     * **********************************************************************************************
     * Aggregate sales per item per location
     * **********************************************************************************************
     */
    PCollection<StockAggregation> transactionPerProductAndLocation =
      transactionWithStoreLoc.apply(new TransactionPerProductAndLocation());
    
    PCollection<StockAggregation> inventoryTransactionPerProduct =
      transactionPerProductAndLocation.apply(
        new CountGlobalStockFromTransaction(Duration.standardSeconds(5)));
    
    /**
     * **********************************************************************************************
     * Process Stock stream
     * **********************************************************************************************
     */
    PCollection<String> inventoryJSON = p.apply(
      "ReadStockStream",
      new ReadPubSubMsgPayLoadAsString(options.getInventoryPubSubSubscriptions()));
    
    PCollection<Stock.StockEvent> inventory = inventoryJSON.apply(new StockProcessing());
    
    /**
     * **********************************************************************************************
     * Aggregate Inventory delivery per item per location
     * **********************************************************************************************
     */
    PCollection<StockAggregation> incomingStockPerProductLocation =
      inventory.apply(new CountIncomingStockPerProductLocation(Duration.standardSeconds(5)));
    
    PCollection<StockAggregation> incomingStockPerProduct =
      incomingStockPerProductLocation.apply(
        new CountGlobalStockUpdatePerProduct(Duration.standardSeconds(5)));
    
    /**
     * **********************************************************************************************
     * Write Stock Aggregates - Combine Transaction / Inventory
     * **********************************************************************************************
     */
    PCollection<StockAggregation> inventoryLocationUpdates =
      PCollectionList.of(transactionPerProductAndLocation)
        .and(inventoryTransactionPerProduct)
        .apply(Flatten.pCollections());
    
    PCollection<StockAggregation> inventoryGlobalUpdates =
      PCollectionList.of(inventoryTransactionPerProduct)
        .and(incomingStockPerProduct)
        .apply(Flatten.pCollections());
    
    /* TODO (davit): write to FG
    inventoryLocationUpdates.apply(
      WriteAggregationToBigQuery.create("StoreStockEvent", Duration.standardSeconds(10)));
    
    inventoryGlobalUpdates.apply(
      WriteAggregationToBigQuery.create("GlobalStockEvent", Duration.standardSeconds(10)));
     */
    
    /**
     * **********************************************************************************************
     * Send Inventory updates to PubSub
     * **********************************************************************************************
     */
    PCollection<String> stockUpdates =
      inventoryGlobalUpdates.apply(
        "ConvertToPubSub", MapElements.into(TypeDescriptors.strings()).via(Object::toString));
  
    stockUpdates.apply(PubsubIO.writeStrings().to(options.getAggregateStockPubSubOutputTopic()));
    
    p.run();
  }
  
  public static void main(String[] args) throws Exception {
    
    RetailPipelineOptions options =
      PipelineOptionsFactory.fromArgs(args).withValidation().as(RetailPipelineOptions.class);
    Pipeline p = Pipeline.create(options);
    
    new RetailDataProcessingPipeline().startRetailPipeline(p);
  }
}
