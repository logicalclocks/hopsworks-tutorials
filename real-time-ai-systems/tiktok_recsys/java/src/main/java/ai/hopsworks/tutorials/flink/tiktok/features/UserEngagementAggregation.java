package  ai.hopsworks.tutorials.flink.tiktok.features;

import ai.hopsworks.tutorials.flink.tiktok.utils.TikTokInteractions;
import org.apache.flink.api.common.functions.AggregateFunction;

import java.time.Instant;

public class UserEngagementAggregation
        implements AggregateFunction<TikTokInteractions, UserWindowAggregationSchema, UserWindowAggregationSchema> {

  public UserEngagementAggregation() {
  }

  @Override
  public UserWindowAggregationSchema createAccumulator() {
    return new UserWindowAggregationSchema();
  }
  
  @Override
  public UserWindowAggregationSchema add(TikTokInteractions record, UserWindowAggregationSchema
          accumulator) {

    accumulator.setUserId(record.getUserId());
    accumulator.setInteractionMonth(record.getInteractionMonth());
    accumulator.setCategoryId(record.getCategoryId());

    // to measure latency, will be overwritten later
    accumulator.setWindowEndTime(record.getProcessStart());

    switch(record.getInteractionType()) {
      case "like":
        accumulator.setLikeCount(engagementDefaultValue(accumulator.getLikeCount()) + 1);
        break;
      case "dislike":
        accumulator.setDislikeCount(engagementDefaultValue(accumulator.getDislikeCount()) + 1);
        break;
      case "view":
        accumulator.setViewCount(engagementDefaultValue(accumulator.getViewCount()) + 1);
        break;
      case "comment":
        accumulator.setCommentCount(engagementDefaultValue(accumulator.getCommentCount()) + 1);
        break;
      case "share":
        accumulator.setShareCount(engagementDefaultValue(accumulator.getShareCount()) + 1);
        break;
      case "skip":
        accumulator.setSkipCount(engagementDefaultValue(accumulator.getShareCount()) + 1);
        break;
    }
    accumulator.setTotalWatchTime(engagementDefaultValue(accumulator.getShareCount()) +
            engagementDefaultValue(record.getWatchTime()));

    return accumulator;
  }
  
  @Override
  public UserWindowAggregationSchema getResult(UserWindowAggregationSchema accumulator) {
    UserWindowAggregationSchema userWindowAggregationSchema = new UserWindowAggregationSchema();
    userWindowAggregationSchema.setUserId(accumulator.getUserId());
    userWindowAggregationSchema.setInteractionMonth(accumulator.getInteractionMonth());

    userWindowAggregationSchema.setLikeCount(engagementDefaultValue(accumulator.getLikeCount()));
    userWindowAggregationSchema.setLikeCount(engagementDefaultValue(accumulator.getLikeCount()));
    userWindowAggregationSchema.setViewCount(engagementDefaultValue(accumulator.getViewCount()));
    userWindowAggregationSchema.setCommentCount(engagementDefaultValue(accumulator.getCommentCount()));
    userWindowAggregationSchema.setShareCount(engagementDefaultValue(accumulator.getShareCount()));
    userWindowAggregationSchema.setSkipCount(engagementDefaultValue(accumulator.getSkipCount()));
    userWindowAggregationSchema.setTotalWatchTime(engagementDefaultValue(accumulator.getTotalWatchTime()));
    return userWindowAggregationSchema;
  }
  
  @Override
  public UserWindowAggregationSchema merge(UserWindowAggregationSchema accumulator,
                                           UserWindowAggregationSchema accumulator1) {
    accumulator.setLikeCount(engagementDefaultValue(accumulator.getLikeCount()) +
            engagementDefaultValue(accumulator1.getLikeCount()));
    accumulator.setDislikeCount(engagementDefaultValue(accumulator.getDislikeCount()) +
            engagementDefaultValue(accumulator1.getDislikeCount()));
    accumulator.setViewCount(engagementDefaultValue(accumulator.getViewCount()) +
            engagementDefaultValue(accumulator1.getViewCount()));
    accumulator.setCommentCount(engagementDefaultValue(accumulator.getCommentCount()) +
            engagementDefaultValue(accumulator1.getCommentCount()));
    accumulator.setShareCount(engagementDefaultValue(accumulator.getShareCount()) +
            engagementDefaultValue(accumulator1.getShareCount()));
    accumulator.setSkipCount(engagementDefaultValue(accumulator.getShareCount()) +
            engagementDefaultValue(accumulator1.getShareCount()));
    accumulator.setTotalWatchTime(engagementDefaultValue(accumulator.getTotalWatchTime()) +
            engagementDefaultValue(accumulator1.getTotalWatchTime()));
    return accumulator;
  }

  private Long engagementDefaultValue(Long engagementValue) {
    return engagementValue == null ? 0: engagementValue;
  }
}
