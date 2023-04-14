package com.hopsworks.tutorials.beam.clickstreampipe.aggregations;

import com.google.auto.value.AutoValue;
import javax.annotation.Nullable;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;
import org.apache.beam.sdk.schemas.annotations.SchemaFieldName;

@AutoValue
@DefaultSchema(AutoValueSchema.class)
@Experimental
public abstract class StockAggregation {
  
  @Nullable
  public abstract Long getDurationMS();
  
  @Nullable
  public abstract Long getStartTime();
  
  @Nullable
  @SchemaFieldName("product_id")
  public abstract Integer getProductId();
  
  @Nullable
  @SchemaFieldName("store_id")
  public abstract Integer getStoreId();
  
  @Nullable
  public abstract Long getCount();
  
  public abstract StockAggregation.Builder toBuilder();
  
  public static StockAggregation.Builder builder() {
    return new AutoValue_StockAggregation.Builder();
  }
  
  @AutoValue.Builder
  public abstract static class Builder {
    
    public abstract Builder setDurationMS(Long value);
    
    public abstract Builder setStartTime(Long value);
    
    public abstract Builder setProductId(Integer value);
    
    public abstract Builder setStoreId(Integer value);
    
    public abstract Builder setCount(Long value);
    
    public abstract StockAggregation build();
  }
}
