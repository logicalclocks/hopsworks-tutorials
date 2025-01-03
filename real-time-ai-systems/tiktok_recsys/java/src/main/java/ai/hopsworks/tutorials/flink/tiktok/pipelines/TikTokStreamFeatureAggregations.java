package ai.hopsworks.tutorials.flink.tiktok.pipelines;

import ai.hopsworks.tutorials.flink.tiktok.features.SourceInteractions;
import ai.hopsworks.tutorials.flink.tiktok.features.UserWindowAggregationSchema;
import ai.hopsworks.tutorials.flink.tiktok.features.UserEngagementAggregation;
import ai.hopsworks.tutorials.flink.tiktok.features.UserEngagementProcessWindow;
import ai.hopsworks.tutorials.flink.tiktok.features.VideoWindowAggregationSchema;
import ai.hopsworks.tutorials.flink.tiktok.features.VideoEngagementAggregation;
import ai.hopsworks.tutorials.flink.tiktok.features.VideoEngagementProcessWindow;
import ai.hopsworks.tutorials.flink.tiktok.simulators.InteractionsGenerator;
import ai.hopsworks.tutorials.flink.tiktok.utils.TikTokInteractions;

import com.logicalclocks.hsfs.flink.FeatureStore;
import com.logicalclocks.hsfs.flink.HopsworksConnection;
import com.logicalclocks.hsfs.flink.StreamFeatureGroup;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.connector.source.util.ratelimit.RateLimiterStrategy;
import org.apache.flink.connector.datagen.source.DataGeneratorSource;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

public class TikTokStreamFeatureAggregations {

  public static final int CHECKPOINTING_INTERVAL_MS = 5000;
  private static final String JOB_NAME = "TikTok Streaming Pipeline";

  private FeatureStore featureStore;

  public TikTokStreamFeatureAggregations() throws Exception {
    //get feature store handle
    HopsworksConnection hopsworksConnection = HopsworksConnection.builder().build();

    featureStore = hopsworksConnection.getFeatureStore();
  }

  public void stream(Long maxId, Long recordsPerSecond, Integer parallelism) throws Exception {

    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.setParallelism(parallelism);

    // Setup the sliding window aggregations 5, 10, 60 minutes
    //interactionSlidingWindow( env,60, 30, maxId, recordsPerSecond, parallelism);
    interactionSlidingWindow( env,10, 5, maxId, recordsPerSecond, parallelism);

    env.execute(JOB_NAME);
    //env.enableCheckpointing(CHECKPOINTING_INTERVAL_MS);
    env.setRestartStrategy(RestartStrategies.noRestart());
  }

  private void interactionSlidingWindow(StreamExecutionEnvironment env,
                                        int windowSizeMinutes,
                                        int slideSizeMinutes,
                                        Long maxId,
                                        Long recordsPerSecond,
                                        int parallelism) throws Exception {

    // Define time for start
    Instant now = Instant.now();
    // Subtract 2 weeks from the current instant
    Instant startTime = now.minus(7, ChronoUnit.DAYS);

    // get or create stream feature group
    StreamFeatureGroup interactionsFeatureGroup = featureStore.getStreamFeatureGroup("interactions", 1);
    StreamFeatureGroup userWindowAgg = featureStore.getStreamFeatureGroup("user_window_agg_1h", 1);
    StreamFeatureGroup videoWindowAgg = featureStore.getStreamFeatureGroup("video_window_agg_1h", 1);

    WatermarkStrategy<TikTokInteractions> customWatermark = WatermarkStrategy
        .<TikTokInteractions>forBoundedOutOfOrderness(Duration.ofSeconds(30))
        .withTimestampAssigner((event, timestamp) -> event.getInteractionDate());

    DataGeneratorSource<TikTokInteractions> generatorSource =
              new DataGeneratorSource<>(
                      new InteractionsGenerator(maxId, startTime),
                      Long.MAX_VALUE,
                      RateLimiterStrategy.perSecond(recordsPerSecond),
                      TypeInformation.of(TikTokInteractions.class));

    DataStream<TikTokInteractions> simEvents =
              env.fromSource(generatorSource,
                              WatermarkStrategy.noWatermarks(),
                              "Generator Source")
            .setParallelism(parallelism)
            .rescale()
            .rebalance();

    // define feature aggregate streams
    DataStream<SourceInteractions> sourceInteractions =
            simEvents
            .keyBy(TikTokInteractions::getUserId)
                    .map((MapFunction<TikTokInteractions, SourceInteractions>) tikTokInteractions -> {
              SourceInteractions sourceInteractions1 = new SourceInteractions();
              sourceInteractions1.setId(tikTokInteractions.getInteractionId());
              sourceInteractions1.setUserId(tikTokInteractions.getUserId());
              sourceInteractions1.setVideoId(tikTokInteractions.getVideoId());
              sourceInteractions1.setCategoryId(tikTokInteractions.getCategoryId());
              sourceInteractions1.setInteractionType(tikTokInteractions.getInteractionType());
              sourceInteractions1.setInteractionDate(tikTokInteractions.getInteractionDate() * 1000);
              sourceInteractions1.setInteractionMonth(tikTokInteractions.getInteractionMonth());
              sourceInteractions1.setWatchTime(tikTokInteractions.getWatchTime());
              return sourceInteractions1;
            });

      DataStream<UserWindowAggregationSchema> userAggregationStream =
            simEvents.assignTimestampsAndWatermarks(customWatermark)
            .keyBy(TikTokInteractions::getUserId)
            .window(SlidingEventTimeWindows.of(Time.minutes(windowSizeMinutes), Time.minutes(slideSizeMinutes)))
            .aggregate(new UserEngagementAggregation(), new UserEngagementProcessWindow());

      DataStream<VideoWindowAggregationSchema> videoAggregationStream =
            simEvents.assignTimestampsAndWatermarks(customWatermark)
            .keyBy(TikTokInteractions::getVideoId)
            .window(SlidingEventTimeWindows.of(Time.minutes(windowSizeMinutes), Time.minutes(slideSizeMinutes)))
            .aggregate(new VideoEngagementAggregation(), new VideoEngagementProcessWindow());

    // insert streams
    interactionsFeatureGroup.insertStream(sourceInteractions);
    userWindowAgg.insertStream(userAggregationStream);
    videoWindowAgg.insertStream(videoAggregationStream);
  }
}
