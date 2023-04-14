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
 *       "item_name": "Donut Friday Scented T-Shirt",
 *       "item_id": "67890",
 *       "price": 33.75,
 *       "item_brand": "Google",
 *       "item_category": "Apparel",
 *       "item_category_2": "Mens",
 *       "item_category_3": "Shirts",
 *       "item_category_4": "Tshirts",
 *       "item_variant": "Black",
 *       "item_list_name": "Search Results",
 *       "item_list_id": "SR123",
 *       "index": 1,
 *       "quantity": 2
 *     }
 *
 * }</pre>
 */
@AutoValue
@DefaultSchema(AutoValueSchema.class)
public abstract class Item {
  
  @SchemaFieldName("item_name")
  public @Nullable abstract String getItemName();
  
  @SchemaFieldName("item_id")
  public @Nullable abstract String getItemId();
  
  @SchemaFieldName("price")
  public @Nullable abstract Float getPrice();
  
  @SchemaFieldName("item_brand")
  public @Nullable abstract String getItemBrand();
  
  @SchemaFieldName("item_category")
  public @Nullable abstract String getItemCat01();
  
  @SchemaFieldName("item_category_2")
  public @Nullable abstract String getItemCat02();
  
  @SchemaFieldName("item_category_3")
  public @Nullable abstract String getItemCat03();
  
  @SchemaFieldName("item_category_4")
  public @Nullable abstract String getItemCat04();
  
  @SchemaFieldName("item_category_5")
  public @Nullable abstract String getItemCat05();
  
  @SchemaFieldName("item_variant")
  public @Nullable abstract String getItemVariant();
  
  @SchemaFieldName("item_list_name")
  public @Nullable abstract String getItemListName();
  
  @SchemaFieldName("item_list_id")
  public @Nullable abstract String getItemListId();
  
  @SchemaFieldName("index")
  public @Nullable abstract Integer getIndex();
  
  @SchemaFieldName("quantity")
  public @Nullable abstract Integer getQuantity();
  
  public static Builder builder() {
    return new AutoValue_Item.Builder();
  }
  
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setItemName(String newItemName);
    
    public abstract Builder setItemId(String newItemId);
    
    public abstract Builder setPrice(Float newPrice);
    
    public abstract Builder setItemBrand(String newItemBrand);
    
    public abstract Builder setItemCat01(String newItemCat01);
    
    public abstract Builder setItemCat02(String newItemCat02);
    
    public abstract Builder setItemCat03(String newItemCat03);
    
    public abstract Builder setItemCat04(String newItemCat04);
    
    public abstract Builder setItemCat05(String newItemCat05);
    
    public abstract Builder setItemVariant(String newItemVariant);
    
    public abstract Builder setItemListName(String newItemListName);
    
    public abstract Builder setItemListId(String newItemListId);
    
    public abstract Builder setIndex(Integer newIndex);
    
    public abstract Builder setQuantity(Integer newQuantity);
    
    public abstract Item build();
  }
}
