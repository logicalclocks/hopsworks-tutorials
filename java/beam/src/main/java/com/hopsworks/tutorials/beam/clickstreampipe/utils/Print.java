package com.hopsworks.tutorials.beam.clickstreampipe.utils;

import java.io.IOException;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.transforms.DoFn;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Experimental
public class Print<T> extends DoFn<T, String> {
  
  private static final Logger LOG = LoggerFactory.getLogger(Print.class);
  
  String message;
  
  public Print(String message) {
    this.message = message;
  }
  
  @ProcessElement
  public void process(@Element T row) throws IOException {
    
    LOG.info(message + row.toString());
  }
}
