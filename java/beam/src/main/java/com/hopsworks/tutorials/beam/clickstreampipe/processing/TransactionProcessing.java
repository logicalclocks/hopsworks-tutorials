package com.hopsworks.tutorials.beam.clickstreampipe.processing;

import java.util.Map;

import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.StoreLocations;
import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.EnrichTransactionWithStoreLocation;
import com.hopsworks.tutorials.beam.clickstreampipe.options.RetailPipelineOptions;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Dimensions;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Transaction;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.JSONUtils;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.windowing.FixedWindows;
import org.apache.beam.sdk.transforms.windowing.Window;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.PCollectionView;
import org.joda.time.Duration;

@Experimental
public class TransactionProcessing
  extends PTransform<PCollection<String>, PCollection<Transaction.TransactionEvent>> {
  
  @Override
  public PCollection<Transaction.TransactionEvent> expand(PCollection<String> input) {
    
    RetailPipelineOptions options =
      input.getPipeline().getOptions().as(RetailPipelineOptions.class);
    
    /**
     * **********************************************************************************************
     * Convert to Transactions Object
     * **********************************************************************************************
     */
    PCollection<Transaction.TransactionEvent> transactions =
      input.apply(JSONUtils.ConvertJSONtoPOJO.create(Transaction.TransactionEvent.class));
    
    /**
     * **********************************************************************************************
     * Validate & Enrich Transactions
     * **********************************************************************************************
     */
    PCollectionView<Map<Integer, Dimensions.StoreLocation>> storeLocationSideinput =
      input
        .getPipeline()
        .apply(
          StoreLocations.create(
            Duration.standardMinutes(10), options.getStoreLocationBigQueryTableRef()));
    
    PCollection<Transaction.TransactionEvent> transactionWithStoreLoc =
      transactions.apply(EnrichTransactionWithStoreLocation.create(storeLocationSideinput));
    
    /**
     * **********************************************************************************************
     * Store Corrected Transaction Data To DW
     * **********************************************************************************************
     */
    
    // TODO (Davit): write online FG
    
    return transactionWithStoreLoc.apply(Window.into(FixedWindows.of(Duration.standardSeconds(5))));
  }
}
