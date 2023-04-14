package com.hopsworks.tutorials.beam.clickstreampipe.aggregations;

import javax.annotation.Nullable;

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
public class CountGlobalStockUpdatePerProduct
  extends PTransform<PCollection<StockAggregation>, PCollection<StockAggregation>> {
  
  Duration duration;
  
  public CountGlobalStockUpdatePerProduct(Duration duration) {
    this.duration = duration;
  }
  
  public CountGlobalStockUpdatePerProduct(@Nullable String name, Duration duration) {
    super(name);
    this.duration = duration;
  }
  
  @Override
  public PCollection<StockAggregation> expand(PCollection<StockAggregation> input) {
    return input
      .apply("SelectProductID", Select.<StockAggregation>fieldNames("product_id"))
      .apply(
        Group.<Row>byFieldNames("product_id")
          .aggregateField("product_id", Count.<Integer>combineFn(), "count"))
      .apply("SelectProductIdCount", Select.<Row>fieldNames("key.product_id", "value.count"))
      .apply(
        AddFields.<Row>create()
          .field("store_id", FieldType.INT32)
          .field("durationMS", FieldType.INT64)
          .field("startTime", FieldType.INT64))
      .apply(Convert.to(StockAggregation.class))
      .apply(new CreateStockAggregatorMetadata(duration.getMillis()));
  }
}
