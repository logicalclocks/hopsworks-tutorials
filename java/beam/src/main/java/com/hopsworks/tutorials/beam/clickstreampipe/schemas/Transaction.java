package com.hopsworks.tutorials.beam.clickstreampipe.schemas;

import com.google.auto.value.AutoValue;
import javax.annotation.Nullable;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;
import org.apache.beam.sdk.schemas.annotations.SchemaFieldName;

/** A transaction is a purchase, either in-store or via the website / mobile application. */
@Experimental
public class Transaction {
  
  @AutoValue
  @DefaultSchema(AutoValueSchema.class)
  public abstract static class TransactionEvent {
    @SchemaFieldName("timestamp")
    public abstract @Nullable Long getTimestamp();
    
    @SchemaFieldName("uid")
    public abstract @Nullable Integer getUid();
    
    @SchemaFieldName("order_number")
    public abstract @Nullable String getOrderNumber();
    
    @SchemaFieldName("user_id")
    public abstract @Nullable Integer getUserId();
    
    @SchemaFieldName("store_id")
    public abstract @Nullable Integer getStoreId();
    
    @SchemaFieldName("time_of_sale")
    public abstract @Nullable Long getTimeOfSale();
    
    @SchemaFieldName("department_id")
    public abstract @Nullable Integer getDepartmentId();
    
    @SchemaFieldName("product_id")
    public abstract @Nullable Integer getProductId();
    
    @SchemaFieldName("product_count")
    public abstract @Nullable Integer getProductCount();
    
    @SchemaFieldName("price")
    public abstract @Nullable Float getPrice();
    
    public abstract @Nullable
    Dimensions.StoreLocation getStoreLocation();
    
    public abstract TransactionEvent.Builder toBuilder();
    
    public static TransactionEvent.Builder builder() {
      return new AutoValue_Transaction_TransactionEvent.Builder();
    }
    
    @AutoValue.Builder
    public abstract static class Builder {
      public abstract Builder setTimestamp(Long value);
      
      public abstract Builder setUid(Integer value);
      
      public abstract Builder setOrderNumber(String value);
      
      public abstract Builder setUserId(Integer value);
      
      public abstract Builder setStoreId(Integer value);
      
      public abstract Builder setTimeOfSale(Long value);
      
      public abstract Builder setDepartmentId(Integer value);
      
      public abstract Builder setProductId(Integer value);
      
      public abstract Builder setProductCount(Integer value);
      
      public abstract Builder setPrice(Float value);
      
      public abstract Builder setStoreLocation(Dimensions.StoreLocation value);
      
      public abstract TransactionEvent build();
    }
  }
}
