package com.hopsworks.tutorials.beam.clickstreampipe.validation;

import java.util.Collection;
import org.apache.beam.sdk.schemas.Schema;
import org.apache.beam.sdk.schemas.Schema.FieldType;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.values.Row;

public class ValidationUtils {
  public static Schema getValidationWrapper(Schema rowSchema) {
    
    return Schema.builder()
      .addRowField("data", rowSchema)
      .addField("errors", FieldType.array(FieldType.STRING).withNullable(true))
      .build();
  }
  
  public static class ValidationRouter extends DoFn<Row, Row> {
    
    @ProcessElement
    public void process(@Element Row input, MultiOutputReceiver o) {
      
      Collection<Object> errors = input.getArray("errors");
      
      if (errors == null || errors.size() < 1) {
        o.get(ValidateAndCorrectCSEvt.MAIN).output(input);
        return;
      }
      o.get(ValidateAndCorrectCSEvt.NEEDS_CORRECTIONS).output(input);
    }
  }
}
