package com.hopsworks.tutorials.beam.clickstreampipe.validation;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Optional;

import com.google.common.collect.ImmutableList;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.ErrorMsg;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.values.Row;
import org.apache.beam.vendor.guava.v26_0_jre.com.google.common.base.Preconditions;
import org.joda.time.Instant;

/**
 * Will validate each event and out put
 *
 * <p>1 - Healthy events
 *
 * <p>2 - Tagged events which have a missing Items information
 */
public class ValidateEventItems extends DoFn<Row, Row> {
  
  public static final String CORRECTION_ITEM = "CORR_ITEM";
  
  @ProcessElement
  public void process(@Element Row input, @Timestamp Instant timestamp, MultiOutputReceiver o) {
    
    // ****************************** Check Items within events
    
    Row data = input.getRow("data");
    
    Preconditions.checkNotNull(data);
    
    // If the event is of a type that needs Item to be present, do checks
    if (chkItemRequired(data)) {
      
      Collection<Row> items = data.getRow("ecommerce").getArray("items");
      // If no items this is not recoverable, send to dead letter.
      if (items == null || items.size() == 0) {
        
        ErrorMsg errorMsg =
          ErrorMsg.builder()
            .setData(input.toString())
            .setError("Event requires item to be set, but not set")
            .setTimestamp(timestamp)
            .setTransform(ValidateEventItems.class.getCanonicalName())
            .build();
        
        o.get(ValidateAndCorrectCSEvt.DEAD_LETTER).output(errorMsg);
        return;
      }
      
      // If item has fields missing this is recoverable, add correction tag
      
      if (chkItemIsInvalid(items)) {
        ArrayList<Object> errorList = new ArrayList<>();
        Optional.ofNullable(input.getArray("errors"))
          .orElse(new ArrayList<>())
          .forEach(x -> errorList.add(x));
        
        errorList.add(CORRECTION_ITEM);
        
        o.get(ValidateAndCorrectCSEvt.MAIN)
          .output(Row.fromRow(input).withFieldValue("errors", errorList).build());
        
        return;
      }
    }
    o.get(ValidateAndCorrectCSEvt.MAIN).output(input);
  }
  
  boolean chkItemIsInvalid(Collection<Row> items) {
    
    // If this is a valid event check that the item is populated correctly
    
    for (Row item : items) {
      if (item.getString("item_name") == null) {
        return true;
      }
      
      if (item.getString("item_brand") == null) {
        return true;
      }
      
      if (item.getString("item_category") == null) {
        return true;
      }
    }
    
    return false;
  }
  
  boolean chkItemRequired(Row input) {
    
    return ImmutableList.of("add_to_cart", "purchase").contains(input.getString("event"));
  }
}
