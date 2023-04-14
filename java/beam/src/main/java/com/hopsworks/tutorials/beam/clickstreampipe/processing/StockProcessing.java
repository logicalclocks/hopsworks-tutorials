package com.hopsworks.tutorials.beam.clickstreampipe.processing;

import com.hopsworks.tutorials.beam.clickstreampipe.options.RetailPipelineOptions;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Stock;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.JSONUtils;
import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.windowing.FixedWindows;
import org.apache.beam.sdk.transforms.windowing.Window;
import org.apache.beam.sdk.values.PCollection;
import org.joda.time.Duration;

@Experimental
public class StockProcessing extends PTransform<PCollection<String>, PCollection<Stock.StockEvent>> {
  
  @Override
  public PCollection<Stock.StockEvent> expand(PCollection<String> input) {
    Pipeline p = input.getPipeline();
    
    RetailPipelineOptions options = p.getOptions().as(RetailPipelineOptions.class);
    
    /**
     * **********************************************************************************************
     * Validate Inventory delivery
     * **********************************************************************************************
     */
    PCollection<Stock.StockEvent> inventory =
      input.apply(JSONUtils.ConvertJSONtoPOJO.create(Stock.StockEvent.class));
    
    /**
     * **********************************************************************************************
     * Write Store Corrected Inventory Data To DW
     * **********************************************************************************************
     */
    // TODO (davit) write to FG, but need to convert to Row

    
    return inventory.apply(Window.into(FixedWindows.of(Duration.standardSeconds(5))));
  }
}
