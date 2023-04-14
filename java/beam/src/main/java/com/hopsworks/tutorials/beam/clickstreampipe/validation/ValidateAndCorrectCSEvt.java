package com.hopsworks.tutorials.beam.clickstreampipe.validation;

import javax.annotation.Nullable;

import com.google.common.collect.ImmutableList;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.DeadLetterSink;
import com.hopsworks.tutorials.beam.clickstreampipe.utils.ErrorMsg;
import com.hopsworks.tutorials.beam.clickstreampipe.services.EventDateTimeCorrectionService;
import com.hopsworks.tutorials.beam.clickstreampipe.services.EventItemCorrectionService;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.Schema;
import org.apache.beam.sdk.transforms.Flatten;
import org.apache.beam.sdk.transforms.MapElements;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.PCollectionList;
import org.apache.beam.sdk.values.PCollectionTuple;
import org.apache.beam.sdk.values.Row;
import org.apache.beam.sdk.values.TupleTag;
import org.apache.beam.sdk.values.TupleTagList;
import org.apache.beam.sdk.values.TypeDescriptors;

/**
 * Clean clickstream:
 *
 * <p>Check if uid is null, check that there is a session-id, if both are missing send to dead
 * letter queue.
 *
 * <p>Check if lat / long are missing, if they are look up user in the user table.
 */
@Experimental
public class ValidateAndCorrectCSEvt extends PTransform<PCollection<Row>, PCollection<Row>> {
  
  public static final TupleTag<Row> MAIN = new TupleTag<Row>() {
  };
  
  public static final TupleTag<ErrorMsg> DEAD_LETTER = new TupleTag<ErrorMsg>() {
  };
  
  public static final TupleTag<Row> NEEDS_CORRECTIONS = new TupleTag<Row>() {
  };
  
  private final DeadLetterSink.SinkType sinkType;
  
  public ValidateAndCorrectCSEvt(DeadLetterSink.SinkType sinkType) {
    this.sinkType = sinkType;
  }
  
  public ValidateAndCorrectCSEvt(@Nullable String name, DeadLetterSink.SinkType sinkType) {
    super(name);
    this.sinkType = sinkType;
  }
  
  @Override
  public PCollection<Row> expand(PCollection<Row> input) {
    
    // Chain the validation steps
    
    Schema wrapperSchema = ValidationUtils.getValidationWrapper(input.getSchema());
    
    // First we wrap the object
    PCollection<Row> wrappedInput =
      input
        .apply(
          "AddWrapper",
          MapElements.into(TypeDescriptors.rows())
            .via(x -> Row.withSchema(wrapperSchema).withFieldValue("data", x).build()))
        .setRowSchema(wrapperSchema);
    
    // Next we chain the object through the validation transforms
    PCollectionTuple validateEventItems =
      wrappedInput.apply(
        "ValidateEventDateTime",
        ParDo.of(new ValidateEventItems())
          .withOutputTags(MAIN, TupleTagList.of(ImmutableList.of(DEAD_LETTER))));
    
    PCollection<Row> validateItems =
      validateEventItems
        .get(MAIN)
        .setRowSchema(wrapperSchema)
        .apply("ValidateEventItems", ParDo.of(new ValidateEventDateTime()))
        .setRowSchema(wrapperSchema);
    
    // DeadLetter issues are not fixable
    PCollectionList.of(validateEventItems.get(DEAD_LETTER))
      .apply("FlattenDeadLetter", Flatten.pCollections())
      .apply("OutputDeadLetterEvents", DeadLetterSink.createSink(sinkType));
    
    // Next we chain the items through the correction transforms, if they have errors
    
    PCollectionTuple validatedCollections =
      validateItems.apply(
        "SplitEventsToBeCorrected",
        ParDo.of(new ValidationUtils.ValidationRouter())
          .withOutputTags(MAIN, TupleTagList.of(ImmutableList.of(NEEDS_CORRECTIONS))));
    
    // Fix bad Items
    PCollection<Row> eventItemsFixed =
      validatedCollections
        .get(NEEDS_CORRECTIONS)
        .setRowSchema(wrapperSchema)
        .apply("CorrectEventItems", ParDo.of(new EventItemCorrectionService()))
        .setRowSchema(wrapperSchema);
    
    // Fix Timestamp
    PCollection<Row> eventDateTimeFixed =
      eventItemsFixed
        .apply("CorrectEventDateTime", ParDo.of(new EventDateTimeCorrectionService()))
        .setRowSchema(wrapperSchema);
    
    PCollection<Row> extractCleanedRows =
      PCollectionList.of(validatedCollections.get(MAIN).setRowSchema(wrapperSchema))
        .and(eventDateTimeFixed)
        .apply("CombineValidAndCorrectedEvents", Flatten.pCollections())
        .apply("RestoreOriginalSchema",
          MapElements.into(TypeDescriptors.rows()).via(x -> x.getRow("data")))
        .setRowSchema(input.getSchema());
    
    return extractCleanedRows;
  }
}
