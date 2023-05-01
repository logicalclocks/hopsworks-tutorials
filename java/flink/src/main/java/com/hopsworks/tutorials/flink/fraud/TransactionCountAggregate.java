package com.hopsworks.tutorials.flink.fraud;

import com.hopsworks.tutorials.flink.SourceTransaction;
import com.hopsworks.tutorials.flink.TransactionAgg;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.java.tuple.Tuple4;

public class TransactionCountAggregate implements AggregateFunction<SourceTransaction,
  Tuple4<Long, Long, Double, Double>, TransactionAgg> {
  
  public TransactionCountAggregate() {
  };
  
  @Override
  public Tuple4<Long, Long, Double, Double> createAccumulator() {
    return new Tuple4<>(0L,0L,0.0,0.0);
  }
  
  @Override
  public Tuple4<Long, Long, Double, Double> add(SourceTransaction record, Tuple4<Long, Long, Double, Double>
    accumulator) {
    return new Tuple4<>(record.getCcNum(), accumulator.f1 + 1, accumulator.f2 + record.getAmount(), 0.0);
  }
  
  @Override
  public TransactionAgg getResult(Tuple4<Long, Long, Double, Double> accumulator) {
    TransactionAgg transactionAgg = new TransactionAgg();
    transactionAgg.setCcNum(accumulator.f0);
    transactionAgg.setNumTransPer10m(accumulator.f1);
    transactionAgg.setAvgAmtPer10m(accumulator.f2/accumulator.f1);
    transactionAgg.setStdevAmtPer10m(accumulator.f3);
    return transactionAgg;
  }
  
  @Override
  public Tuple4<Long, Long, Double, Double> merge(Tuple4<Long, Long, Double, Double> accumulator,
    Tuple4<Long, Long, Double, Double> accumulator1) {
    return new Tuple4<>(accumulator1.f0, accumulator.f1 + accumulator1.f1, accumulator.f2 + accumulator1.f2,
      accumulator.f3 + accumulator1.f3);
  }
}
