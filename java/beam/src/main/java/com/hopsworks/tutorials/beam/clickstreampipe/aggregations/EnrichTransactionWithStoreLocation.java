package com.hopsworks.tutorials.beam.clickstreampipe.aggregations;

import java.util.Map;
import javax.annotation.Nullable;

import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Dimensions;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Transaction;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.PCollectionView;

@Experimental
public class EnrichTransactionWithStoreLocation
  extends PTransform<PCollection<Transaction.TransactionEvent>, PCollection<Transaction.TransactionEvent>> {
  
  PCollectionView<Map<Integer, Dimensions.StoreLocation>> mapPCollectionView;
  
  public EnrichTransactionWithStoreLocation(
    PCollectionView<Map<Integer, Dimensions.StoreLocation>> mapPCollectionView) {
    this.mapPCollectionView = mapPCollectionView;
  }
  
  public EnrichTransactionWithStoreLocation(
    @Nullable String name, PCollectionView<Map<Integer, Dimensions.StoreLocation>> mapPCollectionView) {
    super(name);
    this.mapPCollectionView = mapPCollectionView;
  }
  
  public static EnrichTransactionWithStoreLocation create(
    PCollectionView<Map<Integer, Dimensions.StoreLocation>> mapPCollectionView) {
    return new EnrichTransactionWithStoreLocation(mapPCollectionView);
  }
  
  @Override
  public PCollection<Transaction.TransactionEvent> expand(PCollection<Transaction.TransactionEvent> input) {
    return input.apply(
      "AddStoreLocation",
      ParDo.of(
          new DoFn<Transaction.TransactionEvent, Transaction.TransactionEvent>() {
            @ProcessElement
            public void process(
              @Element
                Transaction.TransactionEvent input,
              @SideInput("mapPCollectionView") Map<Integer, Dimensions.StoreLocation> map,
              OutputReceiver<Transaction.TransactionEvent> o) {
              
              if (map.get(input.getStoreId()) == null) {
                throw new IllegalArgumentException(
                  String.format(" No Store found for id %s", input.getStoreId()));
              }
              
              o.output(
                input.toBuilder().setStoreLocation(map.get(input.getStoreId())).build());
            }
          })
        .withSideInput("mapPCollectionView", mapPCollectionView));
  }
}
