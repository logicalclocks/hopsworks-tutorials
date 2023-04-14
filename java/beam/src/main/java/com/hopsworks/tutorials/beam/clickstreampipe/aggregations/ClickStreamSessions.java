package com.hopsworks.tutorials.beam.clickstreampipe.aggregations;

import com.google.auto.value.AutoValue;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.DeadLetterSink;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.transforms.Group;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.windowing.Sessions;
import org.apache.beam.sdk.transforms.windowing.Window;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.Row;
import org.apache.beam.vendor.guava.v26_0_jre.com.google.common.base.Preconditions;
import org.joda.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This transform creates sessions from the incoming clickstream using the cliendId and
 * SessionWindows. The output is a
 *
 * <pre>{@code
 * Field Name      Field Type
 * key              ROW{clientID:STRING}
 * value	        ITERABLE[ROW[ClickstreamEvent]]
 * }</pre>
 */
@Experimental
@AutoValue
public abstract class ClickStreamSessions extends PTransform<PCollection<Row>, PCollection<Row>> {
  
  private static final Logger LOG = LoggerFactory.getLogger(DeadLetterSink.class);
  
  public abstract Duration getSessionWindowGapDuration();
  
  public abstract Builder toBuilder();
  
  public static ClickStreamSessions create(Duration sessionWindowGapDuration) {
    return builder().setSessionWindowGapDuration(sessionWindowGapDuration).build();
  }
  
  public static Builder builder() {
    return new AutoValue_ClickStreamSessions.Builder();
  }
  
  @AutoValue.Builder
  public abstract static class Builder {
    
    public abstract Builder setSessionWindowGapDuration(Duration newSessionWindowGapDuration);
    
    public abstract ClickStreamSessions build();
  }
  
  public ClickStreamSessions withSessionWindowGapDuration(Duration sessionWindowGapDuration) {
    return this.toBuilder().setSessionWindowGapDuration(sessionWindowGapDuration).build();
  }
  
  @Override
  public PCollection<Row> expand(PCollection<Row> input) {
    
    Preconditions.checkNotNull(
      this.getSessionWindowGapDuration(), "Must set a session gap duration.");
    /*
     * Group.byFiledNames returns a Row object in the format:
     *
     * <pre>{@code
     * Field Name	    Field Type
     * key	            ROW{clientID:STRING}
     * value	        ITERABLE[ROW[ClickstreamEvent]]
     * }</pre>
     */
    return input
      .apply("ClickStreamSessionWindow",
        Window.into(Sessions.withGapDuration(getSessionWindowGapDuration())))
      .apply("GroupByClientId", Group.byFieldNames("client_id"));
  }
}
