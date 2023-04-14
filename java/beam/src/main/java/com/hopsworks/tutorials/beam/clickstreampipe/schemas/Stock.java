package com.hopsworks.tutorials.beam.clickstreampipe.schemas;

import com.google.auto.value.AutoValue;
import javax.annotation.Nullable;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;
import org.apache.beam.sdk.schemas.annotations.SchemaFieldName;

/**
 * A Inventory event is linked to a purchase, either in-store or via the website / mobile
 * application, or a delivery.
 */
@Experimental
public class Stock {
  
  @AutoValue
  @DefaultSchema(AutoValueSchema.class)
  public abstract static class StockEvent {
    public abstract @Nullable Integer getCount();
    
    public abstract @Nullable Integer getSku();
    
    @SchemaFieldName("product_id")
    public abstract @Nullable Integer getProductId();
    
    @SchemaFieldName("store_id")
    public abstract @Nullable Integer getStoreId();
    
    public abstract @Nullable Integer getAisleId();
    
    public abstract @Nullable String getProduct_name();
    
    public abstract @Nullable Integer getDepartmentId();
    
    public abstract @Nullable Float getPrice();
    
    public abstract @Nullable String getRecipeId();
    
    public abstract @Nullable String getImage();
    
    public abstract @Nullable Long getTimestamp();
    
    public abstract Stock.StockEvent.Builder toBuilder();
    
    public static Stock.StockEvent.Builder builder() {
      
      return new AutoValue_Stock_StockEvent.Builder();
    }
    
    @AutoValue.Builder
    public abstract static class Builder {
      public abstract Builder setCount(Integer value);
      
      public abstract Builder setSku(Integer value);
      
      public abstract Builder setProductId(Integer value);
      
      public abstract Builder setStoreId(Integer value);
      
      public abstract Builder setAisleId(Integer value);
      
      public abstract Builder setProduct_name(String value);
      
      public abstract Builder setDepartmentId(Integer value);
      
      public abstract Builder setPrice(Float value);
      
      public abstract Builder setRecipeId(String value);
      
      public abstract Builder setImage(String value);
      
      public abstract Stock.StockEvent.Builder setTimestamp(Long value);
      
      public abstract StockEvent build();
    }
  }
}
