package ai.hopsworks.tutorials.flink.tiktok.features;

import ai.hopsworks.tutorials.flink.tiktok.utils.TikTokInteractions;
import org.apache.flink.api.common.functions.AggregateFunction;

public class VideoEngagementAggregation
        implements AggregateFunction<TikTokInteractions, VideoWindowAggregationSchema, VideoWindowAggregationSchema> {

  public VideoEngagementAggregation() {
  };

  @Override
  public VideoWindowAggregationSchema createAccumulator() {
    return new VideoWindowAggregationSchema();
  }
  
  @Override
  public VideoWindowAggregationSchema add(TikTokInteractions record, VideoWindowAggregationSchema
          accumulator) {
    accumulator.setVideoId(record.getVideoId());
    accumulator.setInteractionMonth(record.getInteractionMonth());

    switch(String.valueOf(record.getInteractionType())) {
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

    return accumulator;
  }
  
  @Override
  public VideoWindowAggregationSchema getResult(VideoWindowAggregationSchema accumulator) {
    VideoWindowAggregationSchema videoWindowAggregationSchema = new VideoWindowAggregationSchema();
    videoWindowAggregationSchema.setVideoId(accumulator.getVideoId());
    videoWindowAggregationSchema.setInteractionMonth(accumulator.getInteractionMonth());

    videoWindowAggregationSchema.setLikeCount(engagementDefaultValue(accumulator.getLikeCount()));
    videoWindowAggregationSchema.setLikeCount(engagementDefaultValue(accumulator.getLikeCount()));
    videoWindowAggregationSchema.setViewCount(engagementDefaultValue(accumulator.getViewCount()));
    videoWindowAggregationSchema.setCommentCount(engagementDefaultValue(accumulator.getCommentCount()));
    videoWindowAggregationSchema.setShareCount(engagementDefaultValue(accumulator.getShareCount()));
    videoWindowAggregationSchema.setSkipCount(engagementDefaultValue(accumulator.getSkipCount()));
    videoWindowAggregationSchema.setTotalWatchTime(engagementDefaultValue(accumulator.getTotalWatchTime()));

    return videoWindowAggregationSchema;
  }
  
  @Override
  public VideoWindowAggregationSchema merge(VideoWindowAggregationSchema accumulator,
                                            VideoWindowAggregationSchema accumulator1) {

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
    accumulator.setTotalWatchTime(engagementDefaultValue(accumulator.getShareCount()) +
            engagementDefaultValue(accumulator1.getTotalWatchTime()));
    return accumulator;
  }

  private Long engagementDefaultValue(Long engagementValue) {
    return engagementValue == null ? 0: engagementValue;
  }
}
