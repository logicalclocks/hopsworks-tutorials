package com.hopsworks.tutorials.beam.clickstreampipe.aggregations;

import javax.annotation.Nullable;

import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Stock;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.Schema.FieldType;
import org.apache.beam.sdk.schemas.transforms.AddFields;
import org.apache.beam.sdk.schemas.transforms.Convert;
import org.apache.beam.sdk.schemas.transforms.Group;
import org.apache.beam.sdk.schemas.transforms.Select;
import org.apache.beam.sdk.transforms.Count;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.Row;
import org.joda.time.Duration;

@Experimental
public class CountIncomingStockPerProductLocation
  extends PTransform<PCollection<Stock.StockEvent>, PCollection<StockAggregation>> {
  
  private Duration duration;
  
  public CountIncomingStockPerProductLocation(Duration duration) {
    this.duration = duration;
  }
  
  public CountIncomingStockPerProductLocation(@Nullable String name, Duration duration) {
    super(name);
    this.duration = duration;
  }
  
  @Override
  public PCollection<StockAggregation> expand(PCollection<Stock.StockEvent> input) {
    return input
      .apply("SelectProductIdStoreId", Select.<Stock.StockEvent>fieldNames("product_id", "store_id"))
      .apply(
        Group.<Row>byFieldNames("product_id", "store_id")
          .aggregateField("*", Count.combineFn(), "count"))
      .apply(
        "SelectProductIdStoreIdCount",
        Select.<Row>fieldNames("key.product_id", "key.store_id", "value.count"))
      .apply(
        AddFields.<Row>create()
          // Need this field until we have @Nullable Schema check
          .field("durationMS", FieldType.INT64)
          .field("startTime", FieldType.INT64))
      .apply(Convert.to(StockAggregation.class))
      .apply(new CreateStockAggregatorMetadata(duration.getMillis()));
  }
}
