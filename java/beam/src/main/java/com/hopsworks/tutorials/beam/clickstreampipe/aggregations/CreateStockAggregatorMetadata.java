package com.hopsworks.tutorials.beam.clickstreampipe.aggregations;

import javax.annotation.Nullable;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.values.PCollection;
import org.joda.time.Instant;

/**
 * Adds metadata to the stock aggregation, for use in downstream systems. The start time of the
 * aggregation, derived from the Window is added as well as the duration, which is passed in as a
 * parameter. This allows for downstream reporting systems to query aggregate values using time
 * boundaries.
 */
@Experimental
public class CreateStockAggregatorMetadata
  extends PTransform<PCollection<StockAggregation>, PCollection<StockAggregation>> {
  
  private Long durationMS;
  
  public static CreateStockAggregatorMetadata create(Long durationMS) {
    return new CreateStockAggregatorMetadata(durationMS);
  }
  
  public CreateStockAggregatorMetadata(Long durationMS) {
    this.durationMS = durationMS;
  }
  
  public CreateStockAggregatorMetadata(@Nullable String name, Long durationMS) {
    super(name);
    this.durationMS = durationMS;
  }
  
  @Override
  public PCollection<StockAggregation> expand(PCollection<StockAggregation> input) {
    
    return input.apply(
      ParDo.of(
        new DoFn<StockAggregation, StockAggregation>() {
          @ProcessElement
          public void process(
            @Element StockAggregation input,
            @Timestamp Instant time,
            OutputReceiver<StockAggregation> o) {
            o.output(
              input
                .toBuilder()
                .setDurationMS(durationMS)
                .setStartTime(time.getMillis() - durationMS + 1)
                .build());
          }
        }));
  }
}
