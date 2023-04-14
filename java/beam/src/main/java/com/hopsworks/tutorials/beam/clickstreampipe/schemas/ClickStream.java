package com.hopsworks.tutorials.beam.clickstreampipe.schemas;

import com.google.auto.value.AutoValue;
import javax.annotation.Nullable;

import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;
import org.apache.beam.sdk.schemas.annotations.SchemaFieldName;

/**
 * Objects used for dealing with clickstreampipe within the pipeline and schemas for I/O of clickstreampipe
 * events. Example events:
 *
 * <p>View Item
 *
 * <pre>{@code
 *     {
 *   "event_datetime":"2020-11-16 22:59:59",
 *   "event": "view_item",
 *   "user_id": "UID00003",
 *   "client_id": "CID00003",
 *   "page":"/product-67890",
 *   "page_previous": "/category-tshirts",
 *   "ecommerce": {
 *     "items": [{
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
 *       "quantity": 1
 *     }]
 *   }
 * }
 *
 *
 * }</pre>
 *
 * add_to_cart
 *
 * <pre>{@code
 *     {
 *   "event_datetime":"2020-11-16 20:59:59",
 *   "event": "add_to_cart",
 *   "user_id": "UID00003",
 *   "client_id": "CID00003",
 *   "page":"/product-67890",
 *   "page_previous": "/category-tshirts",
 *   "ecommerce": {
 *     "items": [{
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
 *     }]
 *   }
 * }
 *
 * }</pre>
 *
 * purchase
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
@Experimental
public class ClickStream {
  
  @AutoValue
  @DefaultSchema(AutoValueSchema.class)
  /**
   * The Clickstream event represents actions that a user has taken on the website or mobile
   * application.
   */
  public abstract static class ClickStreamEvent {
    
    @SchemaFieldName("event_datetime")
    public @Nullable abstract String getEventTime();
    
    @SchemaFieldName("event")
    public @Nullable abstract String getEvent();
    
    @SchemaFieldName("timestamp")
    public @Nullable abstract Long getTimestamp();
    
    @SchemaFieldName("user_id")
    public @Nullable abstract Long getUid();
    
    @SchemaFieldName("client_id")
    public @Nullable abstract String getClientId();
    
    @SchemaFieldName("page")
    public @Nullable abstract String getPage();
    
    @SchemaFieldName("page_previous")
    public @Nullable abstract String getPagePrevious();
    
    @SchemaFieldName("ecommerce")
    public @Nullable abstract Ecommerce getEcommerce();
    
    public abstract Builder toBuilder();
    
    public static Builder builder() {
      return new AutoValue_ClickStream_ClickStreamEvent.Builder();
    }
    
    @AutoValue.Builder
    public abstract static class Builder {
      
      public abstract Builder setEventTime(String value);
      
      public abstract Builder setEvent(String value);
      
      public abstract Builder setTimestamp(Long value);
      
      public abstract Builder setUid(Long value);
      
      public abstract Builder setClientId(String value);
      
      public abstract Builder setPage(String value);
      
      public abstract Builder setPagePrevious(String value);
      
      public abstract Builder setEcommerce(Ecommerce ecommerce);
      
      public abstract ClickStreamEvent build();
    }
  }
  
  // -----------------------------------
  // Schema used for dealing with page views when working with BigTable.
  // -----------------------------------
  
  /** This class hosts the strings used for the row being stored in BigTable. */
  public static class ClickStreamBigTableSchema {
    public static final String PAGE_VIEW_AGGREGATION_COL_FAMILY = "pageViewAgg";
    public static final String PAGE_VIEW_AGGREGATION_COL_PAGE_VIEW_REF = "pageViewRef";
    public static final String PAGE_VIEW_AGGREGATION_COL_PAGE_VIEW_COUNT = "pageViewCount";
  }
  
  @AutoValue
  @DefaultSchema(AutoValueSchema.class)
  public abstract static class PageViewAggregator {
    public @Nullable abstract Long getDurationMS();
    
    public @Nullable abstract Long getStartTime();
    
    public @Nullable abstract String getPage();
    
    public @Nullable abstract Long getCount();
    
    public abstract Builder toBuilder();
    
    public static Builder builder() {
      
      return new AutoValue_ClickStream_PageViewAggregator.Builder();
    }
    
    @AutoValue.Builder
    public abstract static class Builder {
      public abstract Builder setDurationMS(Long value);
      
      public abstract Builder setStartTime(Long value);
      
      public abstract Builder setPage(String value);
      
      public abstract Builder setCount(Long value);
      
      public abstract PageViewAggregator build();
    }
  }
}
