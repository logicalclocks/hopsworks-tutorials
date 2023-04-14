package com.hopsworks.tutorials.beam.clickstreampipe.schemas;

import com.google.auto.value.AutoValue;
import java.util.List;
import javax.annotation.Nullable;

import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;
import org.apache.beam.sdk.schemas.annotations.SchemaFieldName;

@AutoValue
@DefaultSchema(AutoValueSchema.class)
public abstract class Ecommerce {
  
  @SchemaFieldName("items")
  public @Nullable abstract List<Item> getItems();
  
  @SchemaFieldName("purchase")
  public @Nullable abstract Purchase getPurchase();
  
  public static Builder builder() {
    
    return new AutoValue_Ecommerce.Builder();
  }
  
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setItems(List<Item> value);
    
    public abstract Builder setPurchase(Purchase purchase);
    
    public abstract Ecommerce build();
  }
}
