package com.hopsworks.tutorials.beam.clickstreampipe.utils;

import org.apache.beam.sdk.annotations.Experimental;

@Experimental
public class DeploymentAnnotations {
  
  /** Used to indicate a transform will have side effects in deployment life cycle events. */
  public static @interface NoPartialResultsOnDrain {}
  
  public static @interface PartialResultsExpectedOnDrain {}
}
