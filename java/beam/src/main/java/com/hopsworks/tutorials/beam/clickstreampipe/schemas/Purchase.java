package com.hopsworks.tutorials.beam.clickstreampipe.schemas;

import com.google.auto.value.AutoValue;
import javax.annotation.Nullable;
import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;
import org.apache.beam.sdk.schemas.annotations.SchemaFieldName;

/**
 *
 *
 * <pre>{@code
 * {
 *   "event_datetime":"2020-11-16 20:59:59",
 *   "event": "purchase",
 *   "user_id": "UID00001",
 *   "client_id": "CID00003",
 *   "page":"/checkout",
 *   "page_previous": "/order-confirmation",
 *   "ecommerce": {
 *     "purchase": {
 *       "transaction_id": "T12345",
 *       "affiliation": "Online Store",
 *       "value": 35.43,
 *       "tax": 4.90,
 *       "shipping": 5.99,
 *       "currency": "EUR",
 *       "coupon": "SUMMER_SALE",
 *       "items": [{
 *         "item_name": "Triblend Android T-Shirt",
 *         "item_id": "12345",
 *         "item_price": 15.25,
 *         "item_brand": "Google",
 *         "item_category": "Apparel",
 *         "item_variant": "Gray",
 *         "quantity": 1,
 *         "item_coupon": ""
 *       }, {
 *         "item_name": "Donut Friday Scented T-Shirt",
 *         "item_id": "67890",
 *         "item_price": 33.75,
 *         "item_brand": "Google",
 *         "item_category": "Apparel",
 *         "item_variant": "Black",
 *         "quantity": 1
 *       }]
 *     }
 *   }
 * }
 *
 * }</pre>
 */
@AutoValue
@DefaultSchema(AutoValueSchema.class)
public abstract class Purchase {
  
  @SchemaFieldName("transaction_id")
  public @Nullable abstract String getItemName();
  
  @SchemaFieldName("affiliation")
  public @Nullable abstract String getItemId();
  
  @SchemaFieldName("value")
  public @Nullable abstract String getPrice();
  
  @SchemaFieldName("tax")
  public @Nullable abstract String getItemBrand();
  
  @SchemaFieldName("shipping")
  public @Nullable abstract String getItemCat01();
  
  @SchemaFieldName("currency")
  public @Nullable abstract String getItemCat02();
  
  @SchemaFieldName("coupon")
  public @Nullable abstract String getItemCat03();
  
  public static Builder builder() {
    return new AutoValue_Purchase.Builder();
  }
  
  @AutoValue.Builder
  public abstract static class Builder {
    
    public abstract Builder setItemName(String newItemName);
    
    public abstract Builder setItemId(String newItemId);
    
    public abstract Builder setPrice(String newPrice);
    
    public abstract Builder setItemBrand(String newItemBrand);
    
    public abstract Builder setItemCat01(String newItemCat01);
    
    public abstract Builder setItemCat02(String newItemCat02);
    
    public abstract Builder setItemCat03(String newItemCat03);
    
    public abstract Purchase build();
  }
}
