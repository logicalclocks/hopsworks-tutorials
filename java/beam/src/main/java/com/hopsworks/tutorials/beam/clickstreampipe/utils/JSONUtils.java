package com.hopsworks.tutorials.beam.clickstreampipe.utils;

import javax.annotation.Nullable;

import com.google.auto.value.AutoValue;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.metrics.Distribution;
import org.apache.beam.sdk.metrics.Metrics;
import org.apache.beam.sdk.schemas.NoSuchSchemaException;
import org.apache.beam.sdk.schemas.Schema;
import org.apache.beam.sdk.schemas.transforms.Convert;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.JsonToRow;
import org.apache.beam.sdk.transforms.JsonToRow.ParseResult;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.Row;
import org.joda.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Experimental
public class JSONUtils {
  /**
   * Convert an object to a ROW, on failure send JSON String to DeadLetter sink.
   *
   * <p>Thin wrapper around the {@link JsonToRow} utility which takes care of sending data to
   * deadletter sink.
   *
   * @param <T>
   */
  
  /** Convert an object to a POJO, on failure send JSON String to DeadLetter output. */
  @DeploymentAnnotations.NoPartialResultsOnDrain
  @AutoValue
  public abstract static class JSONtoRowWithDeadLetterSink
    extends PTransform<PCollection<String>, PCollection<Row>> {
    
    private static final Logger LOG = LoggerFactory.getLogger(ConvertJSONtoPOJO.class);
    
    abstract @Nullable
    DeadLetterSink.SinkType getSinkType();
    
    abstract Schema getSchema();
    
    @AutoValue.Builder
    public abstract static class Builder {
      public abstract Builder setSinkType(DeadLetterSink.SinkType newSinkType);
      
      public abstract Builder setSchema(Schema newSchema);
      
      public abstract JSONtoRowWithDeadLetterSink build();
    }
    
    public static Builder builder() {
      return new AutoValue_JSONUtils_JSONtoRowWithDeadLetterSink.Builder();
    }
    
    public static JSONtoRowWithDeadLetterSink withSchema(Schema schema) {
      return new AutoValue_JSONUtils_JSONtoRowWithDeadLetterSink.Builder()
        .setSchema(schema)
        .build();
    }
    
    @Override
    public PCollection<Row> expand(PCollection<String> input) {
      Schema errMessageSchema = null;
      
      try {
        errMessageSchema = input.getPipeline().getSchemaRegistry().getSchema(ErrorMsg.class);
      } catch (NoSuchSchemaException e) {
        LOG.error(e.getMessage());
        throw new IllegalArgumentException(
          String.format("Could not find schema for %s", ErrorMsg.class.getCanonicalName()));
      }
      
      ParseResult result =
        input.apply(JsonToRow.withExceptionReporting(getSchema()).withExtendedErrorInfo());
      
      // We need to deal with json strings that have failed to parse.
      
      PCollection<ErrorMsg> errorMsgs =
        result
          .getFailedToParseLines()
          .apply("CreateErrorMessages", ParDo.of(new CreateErrorEvents(errMessageSchema)))
          .setRowSchema(errMessageSchema)
          .apply("ConvertErrMsgToRows", Convert.fromRows(ErrorMsg.class));
      
      if (getSinkType() == DeadLetterSink.SinkType.BIGQUERY) {
        errorMsgs.apply(DeadLetterSink.createSink(getSinkType()));
      } else {
        // Always output parse issues, minimum area will be to logging.
        errorMsgs.apply(DeadLetterSink.createSink(DeadLetterSink.SinkType.LOG));
      }
      // Convert the parsed results to the POJO using Convert operation.
      return result.getResults();
    }
  }
  
  /**
   * Convert an object to a POJO, on failure send JSON String to DeadLetter output.
   *
   * <p>TODO convert to AutoValue for configuration.
   */
  @DeploymentAnnotations.NoPartialResultsOnDrain
  public static class ConvertJSONtoPOJO<T> extends PTransform<PCollection<String>, PCollection<T>> {
    
    private static final Logger LOG = LoggerFactory.getLogger(ConvertJSONtoPOJO.class);
    
    public static <T> ConvertJSONtoPOJO<T> create(Class<T> t) {
      return new ConvertJSONtoPOJO<T>(t, null);
    }
    
    public static <T> ConvertJSONtoPOJO<T> create(Class<T> t, DeadLetterSink.SinkType sinkType) {
      return new ConvertJSONtoPOJO<T>(t, sinkType);
    }
    
    Class<T> clazz;
    DeadLetterSink.SinkType sinkType;
    
    public ConvertJSONtoPOJO(Class<T> clazz, DeadLetterSink.SinkType sinkType) {
      this.clazz = clazz;
      this.sinkType = sinkType;
    }
    
    public ConvertJSONtoPOJO(@Nullable String name, Class<T> clazz, DeadLetterSink.SinkType sinkType) {
      super(name);
      this.clazz = clazz;
      this.sinkType = sinkType;
    }
    
    @Override
    public PCollection<T> expand(PCollection<String> input) {
      Schema objectSchema = null, errMessageSchema = null;
      
      try {
        objectSchema = input.getPipeline().getSchemaRegistry().getSchema(clazz);
      } catch (NoSuchSchemaException e) {
        LOG.error(e.getMessage());
        throw new IllegalArgumentException(
          String.format("Could not find schema for Object of %s", clazz.getCanonicalName()));
      }
      
      try {
        errMessageSchema = input.getPipeline().getSchemaRegistry().getSchema(ErrorMsg.class);
      } catch (NoSuchSchemaException e) {
        LOG.error(e.getMessage());
        throw new IllegalArgumentException(
          String.format("Could not find schema for %s", ErrorMsg.class.getCanonicalName()));
      }
      
      ParseResult result =
        input.apply(JsonToRow.withExceptionReporting(objectSchema).withExtendedErrorInfo());
      
      // We need to deal with json strings that have failed to parse.
      
      PCollection<ErrorMsg> errorMsgs =
        result
          .getFailedToParseLines()
          .apply("CreateErrorRows", ParDo.of(new CreateErrorEvents(errMessageSchema)))
          .setRowSchema(errMessageSchema)
          .apply("ConvertRowsToErrMsg", Convert.fromRows(ErrorMsg.class));
      
      if (sinkType != null) {
        errorMsgs.apply(DeadLetterSink.createSink(sinkType));
      } else {
        // Always output parse issues, minimum area will be to logging.
        errorMsgs.apply(DeadLetterSink.createSink(DeadLetterSink.SinkType.LOG));
      }
      // Convert the parsed results to the POJO using Convert operation.
      PCollection<Row> output = result.getResults();
      return output.apply("ConvertRowsToPOJO", Convert.fromRows(clazz));
    }
  }
  
  private static class CreateErrorEvents extends DoFn<Row, Row> {
    
    private static final String METRIC_NAMESPACE = "JsonConverstion";
    
    private static final String DEAD_LETTER_METRIC_NAME = "JSONParseFailure";
    
    Schema errMessage;
    
    private Distribution jsonConversionErrors =
      Metrics.distribution(METRIC_NAMESPACE, DEAD_LETTER_METRIC_NAME);
    
    public CreateErrorEvents(Schema errMessage) {
      this.errMessage = errMessage;
    }
    
    @ProcessElement
    public void processElement(
      @FieldAccess("line") String jsonString,
      @FieldAccess("err") String errorMessage,
      @Timestamp Instant timestamp,
      OutputReceiver<Row> o) {
      
      jsonConversionErrors.update(1L);
      
      System.out.println(errorMessage);
      
      o.output(
        Row.withSchema(errMessage)
          .withFieldValue("data", jsonString)
          .withFieldValue("error", errorMessage)
          .withFieldValue("timestamp", timestamp)
          .build());
    }
  }
}
