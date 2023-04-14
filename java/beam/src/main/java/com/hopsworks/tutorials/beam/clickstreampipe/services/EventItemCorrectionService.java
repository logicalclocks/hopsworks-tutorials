package com.hopsworks.tutorials.beam.clickstreampipe.services;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Item;
import com.hopsworks.tutorials.beam.clickstreampipe.validation.ValidateEventItems;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.windowing.BoundedWindow;
import org.apache.beam.sdk.values.Row;
import org.joda.time.Instant;

public class EventItemCorrectionService extends DoFn<Row, Row> {
  
  List<_WindowWrappedEvent> cache;
  RetailCompanyServices services;
  
  @Setup
  public void setup() {
    // Starting up super doper heavy service... ;-) well it is just a demo...
    services = new RetailCompanyServices();
    
    // setup our cache, in batch mode this
    cache = new ArrayList<>();
  }
  
  @ProcessElement
  public void process(
    @Element Row input, BoundedWindow w, @Timestamp Instant time, OutputReceiver<Row> o) {
    
    // Pass through if items are not needed by this event.
    
    if (!input.getArray("errors").contains(ValidateEventItems.CORRECTION_ITEM)) {
      o.output(input);
      return;
    }
    
    _WindowWrappedEvent packagedEvent = new _WindowWrappedEvent();
    packagedEvent.eventData = input;
    packagedEvent.eventWindow = w;
    packagedEvent.timestamp = time;
    
    cache.add(packagedEvent);
  }
  
  @FinishBundle
  public void finishBundle(FinishBundleContext fbc) {
    
    if (cache.size() > 0) {
      Map<String, Item> correctedEvents =
        services.convertItemIdsToFullText(
          populateIds(cache), cache.get(0).eventData.getRow("data").getSchema());
      
      // For each row, look up the value in the map and correct
      for (_WindowWrappedEvent event : cache) {
        
        Row row = event.eventData.getRow("data");
        Collection<Row> items = row.getRow("ecommerce").getArray("items");
        List<Row> updatedItems = new ArrayList<>();
        
        for (Row item : items) {
          String itemId = ((Row) item).getValue("item_id");
          Item correctedItem = correctedEvents.get(itemId);
          
          updatedItems.add(
            Row.fromRow(item)
              .withFieldValue("item_name", correctedItem.getItemName())
              .withFieldValue("item_category", correctedItem.getItemCat01())
              .withFieldValue("item_brand", correctedItem.getItemBrand())
              .build());
        }
        
        Row itemsRow =
          Row.fromRow(row.getRow("ecommerce")).withFieldValue("items", updatedItems).build();
        Row newDataRow = Row.fromRow(row).withFieldValue("ecommerce", itemsRow).build();
        
        fbc.output(
          Row.fromRow(event.eventData).withFieldValue("data", newDataRow).build(),
          event.timestamp,
          event.eventWindow);
      }
    }
    // Clear down the cache
    cache.clear();
  }
  
  private List<String> populateIds(List<_WindowWrappedEvent> events) {
    List<String> ids = new ArrayList<>();
    
    // Get a list of all ID's that we need information for.
    events.forEach(
      x ->
        x.eventData
          .getRow("data")
          .getRow("ecommerce")
          .getArray("items")
          .forEach(y -> ids.add(((Row) y).getString("item_id"))));
    
    return ids;
  }
  
  /**
   * When using finish bundle we need information outside of just the element that we wish to
   * output. This is because Beam bundles can have different key / window per bundle.
   */
  private static class _WindowWrappedEvent {
    Row eventData;
    BoundedWindow eventWindow;
    Instant timestamp;
  }
}
