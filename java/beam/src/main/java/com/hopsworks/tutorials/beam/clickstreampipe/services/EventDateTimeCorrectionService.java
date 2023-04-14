package com.hopsworks.tutorials.beam.clickstreampipe.services;

import com.hopsworks.tutorials.beam.clickstreampipe.validation.ValidateEventDateTime;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.values.Row;
import org.apache.beam.sdk.values.Row.FieldValueBuilder;
import org.joda.time.Instant;

public class EventDateTimeCorrectionService extends DoFn<Row, Row> {
  
  @ProcessElement
  public void process(@Element Row input, @Timestamp Instant time, OutputReceiver<Row> o) {
    
    // Pass through if items are not needed by this event.
    
    if (!input.getArray("errors").contains(ValidateEventDateTime.CORRECTION_TIMESTAMP)) {
      o.output(input);
      return;
    }
    
    FieldValueBuilder row = Row.fromRow(input.getRow("data"));
    
    // There are two stations where we can be in this code, the event_datetime did not parse or
    // the time was in the future.
    // In both cases the fix is to set timestamp to be the processing time.
    row.withFieldValue("timestamp", time.getMillis());
    o.output(Row.fromRow(input).withFieldValue("data", row.build()).build());
  }
}
