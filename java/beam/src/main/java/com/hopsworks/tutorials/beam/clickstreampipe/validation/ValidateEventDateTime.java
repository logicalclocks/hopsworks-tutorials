package com.hopsworks.tutorials.beam.clickstreampipe.validation;

import java.util.ArrayList;
import java.util.Optional;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.values.Row;
import org.apache.beam.sdk.values.Row.FieldValueBuilder;
import org.joda.time.DateTime;
import org.joda.time.Instant;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.DateTimeFormatterBuilder;
import org.joda.time.format.DateTimeParser;

/**
 * Will validate each event and out put
 *
 * <p>1 - Healthy events
 *
 * <p>2 - Events which have a bad event DateTime values.
 */
public class ValidateEventDateTime extends DoFn<Row, Row> {
  
  public static final String CORRECTION_TIMESTAMP = "CORR_TIME";
  
  DateTimeFormatter fmt = null;
  
  @Setup
  public void setup() {
    DateTimeParser[] parsers = {
      DateTimeFormat.forPattern("yyyy-MM-dd HH:MM:SS").withZoneUTC().getParser(),
      DateTimeFormat.forPattern("yyyy-MM-dd HH:MM:SSZ").getParser()
    };
    fmt = new DateTimeFormatterBuilder().append(null, parsers).toFormatter();
  }
  
  @ProcessElement
  public void process(@Element Row input, @Timestamp Instant timestamp, OutputReceiver<Row> o) {
    
    boolean errors = false;
    
    Row data = input.getRow("data");
    
    // ****************************** Check DateTime values
    
    // Test that the date of the event is valid based.
    // Test 1 Check Date valid format
    
    FieldValueBuilder row = Row.fromRow(input);
    Long eventTime = null;
    
    try {
      DateTime dateTime = fmt.parseDateTime(data.getString("event_datetime"));
      eventTime = dateTime.toInstant().getMillis();
      row.withFieldValue("timestamp", eventTime);
      // Test 2 Check that the Event time was not set in the future.
      // To check, we compare with processing time (when it was added to PubSub) if after that value
      // we correct
      if (timestamp.getMillis() < eventTime) {
        errors = true;
      }
      
    } catch (Exception ex) {
      errors = true;
    }
    
    if (errors) {
      
      ArrayList<Object> errorList = new ArrayList<>();
      Optional.ofNullable(input.getArray("errors"))
        .orElse(new ArrayList<>())
        .forEach(x -> errorList.add(x));
      
      errorList.add(CORRECTION_TIMESTAMP);
      
      o.output(Row.fromRow(input).withFieldValue("errors", errorList).build());
      return;
    }
    
    o.output(row.build());
  }
}
