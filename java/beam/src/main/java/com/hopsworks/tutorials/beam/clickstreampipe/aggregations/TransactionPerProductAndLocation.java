package com.hopsworks.tutorials.beam.clickstreampipe.aggregations;

import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Dimensions;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Transaction;
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

@Experimental
public class TransactionPerProductAndLocation
  extends PTransform<PCollection<Transaction.TransactionEvent>, PCollection<StockAggregation>> {
  
  @Override
  public PCollection<StockAggregation> expand(PCollection<Transaction.TransactionEvent> input) {
    
    input.getPipeline().getSchemaRegistry().registerPOJO(Dimensions.StoreLocation.class);
    
    PCollection<Row> aggregate =
      input.apply(
        "SelectProductStore", Select.<Transaction.TransactionEvent>fieldNames("product_id", "store_id"));
    
    PCollection<Row> cnt =
      aggregate
        .apply(
          Group.<Row>byFieldNames("product_id", "store_id")
            .aggregateField("store_id", Count.combineFn(), "count"))
        .apply(
          "SelectStoreProductCount",
          Select.fieldNames("key.store_id", "key.product_id", "value.count"))
        .apply(
          AddFields.<Row>create()
            .field("durationMS", FieldType.INT64)
            .field("startTime", FieldType.INT64));
    
    return cnt.apply(Convert.to(StockAggregation.class));
  }
}