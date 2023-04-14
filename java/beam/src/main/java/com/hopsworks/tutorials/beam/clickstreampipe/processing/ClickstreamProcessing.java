package com.hopsworks.tutorials.beam.clickstreampipe.processing;

import com.hopsworks.tutorials.beam.clickstreampipe.utils.DeadLetterSink;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.DeploymentAnnotations;
import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.ClickStreamSessions;
import com.hopsworks.tutorials.beam.clickstreampipe.aggregations.CountViewsPerProduct;
import com.hopsworks.tutorials.beam.clickstreampipe.options.RetailPipelineOptions;
import com.hopsworks.tutorials.beam.clickstreampipe.schemas.ClickStream;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.JSONUtils;
import com.hopsworks.tutorials.beam.clickstreampipe.validation.ValidateAndCorrectCSEvt;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.extensions.avro.schemas.AvroRecordSchema;
import org.apache.beam.sdk.schemas.NoSuchSchemaException;
import org.apache.beam.sdk.schemas.Schema;
import org.apache.beam.sdk.schemas.transforms.Filter;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.transforms.SerializableFunction;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.Row;
import org.apache.beam.sdk.values.TypeDescriptor;
import org.checkerframework.checker.initialization.qual.Initialized;
import org.checkerframework.checker.nullness.qual.NonNull;
import org.checkerframework.checker.nullness.qual.UnknownKeyFor;
import org.joda.time.Duration;
import org.joda.time.Instant;

/**
 * Process clickstream from online stores.
 *
 * <p>Read Click Stream Topic
 *
 * <p>Parse Messages to Beam SCHEMAS
 *
 * <p>Branch 1:
 *
 * <p>Write RAW JSON String Clickstream for storage
 *
 * <p>Branch 2:
 *
 * <p>Clean the data
 *
 * <p>Write Cleaned Data to BigQuery
 *
 * <p>Branch 2.1:
 *
 * <p>Filter out events of type ERROR
 *
 * <p>Count Page Views per product in 5 sec windows
 *
 * <p>Export page view aggregates to BigTable
 *
 * <p>Export page view aggregates to BigQuery
 */
@DeploymentAnnotations.PartialResultsExpectedOnDrain
@Experimental
public class ClickstreamProcessing extends PTransform<PCollection<String>, PCollection<Row>> {
  
  @Override
  public PCollection<Row> expand(PCollection<String> input) {
    
    RetailPipelineOptions options =
      input.getPipeline().getOptions().as(RetailPipelineOptions.class);
    
    Schema csEvtSchema = null;
    
    try {
      csEvtSchema = input.getPipeline().getSchemaRegistry().getSchema(ClickStream.ClickStreamEvent.class);
    } catch (NoSuchSchemaException e) {
      throw new IllegalArgumentException("Unable to get Schema for ClickStreamEvent class.");
    }
    
    /**
     * **********************************************************************************************
     * Parse Messages to SCHEMAS
     * **********************************************************************************************
     */
    PCollection<Row> csEvtRows =
      input.apply(JSONUtils.JSONtoRowWithDeadLetterSink.withSchema(csEvtSchema));
    
    
    /**
     * *********************************************************************************************
     * Clean the data
     *
     * <p>*********************************************************************************************
     */
    PCollection<Row> cleanCSRow =
      csEvtRows.apply(
        new ValidateAndCorrectCSEvt(
          ((options.getTestModeEnabled()) ? DeadLetterSink.SinkType.LOG : DeadLetterSink.SinkType.BIGQUERY)));
    
    /**
     * *********************************************************************************************
     * Filter out events of type ERROR
     *
     * <p>*********************************************************************************************
     */
    PCollection<Row> cleanDataWithOutErrorEvents =
      cleanCSRow.apply(Filter.<Row>create().whereFieldName("event", c -> !c.equals("ERROR")));
    
    /**
     * *********************************************************************************************
     * Count Page Views per product in 5 sec windows
     *
     * <p>*********************************************************************************************
     */
    PCollection<ClickStream.PageViewAggregator> pageViewAggregator =
      cleanDataWithOutErrorEvents.apply(new CountViewsPerProduct(Duration.standardSeconds(5)));

    /**
     * *********************************************************************************************
     * Export page view aggregates to FG
     *
     * <p>*********************************************************************************************
     */
    
    // TODO (davit): write to FG
    pageViewAggregator.apply(
      ParDo.of(
        new DoFn<ClickStream.PageViewAggregator, Row>() {
          @ProcessElement
          public void process(
            @Element ClickStream.PageViewAggregator input, @Timestamp
            Instant time, OutputReceiver<Row> o) {
            // The default timestamp attached to a combined value is the end of the window
            // To find the start of the window we deduct the duration + 1 as beam windows
            // are (start,end] with epsilon of 1 ms
            Row row = new AvroRecordSchema().toRowFunction(TypeDescriptor.of(ClickStream.PageViewAggregator.class))
              .apply(input);
            o.output(row);
          }
        }));
  
  
    /**
     * *********************************************************************************************
     * Sessionize the data using sessionid
     *
     * <p>*********************************************************************************************
     */
    PCollection<Row> sessionizedCS =
      cleanCSRow.apply(ClickStreamSessions.create(Duration.standardMinutes(10)));
  
    /**
     * *********************************************************************************************
     * Write sessionized clickstream to FG
     *
     * <p>*********************************************************************************************
     */
  
    // TODO (davit): write to FG ???
    // sessionizedCS.apply(...)
    
    return cleanDataWithOutErrorEvents;
  }
}
