package com.hopsworks.tutorials.beam.clickstreampipe.utils;

import com.google.auto.value.AutoValue;
import javax.annotation.Nullable;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;
import org.joda.time.Instant;

/** Error Objects for Dead Letter */
@AutoValue
@DefaultSchema(AutoValueSchema.class)
@Experimental
public abstract class ErrorMsg {
  public @Nullable abstract String getTransform();
  
  public @Nullable abstract String getError();
  
  public @Nullable abstract String getData();
  
  public @Nullable abstract Instant getTimestamp();
  
  public abstract Builder toBuilder();
  
  public static Builder builder() {
    return new AutoValue_ErrorMsg.Builder();
  }
  
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setTransform(String value);
    
    public abstract Builder setError(String value);
    
    public abstract Builder setData(String value);
    
    public abstract Builder setTimestamp(Instant value);
    
    public abstract ErrorMsg build();
  }
}
