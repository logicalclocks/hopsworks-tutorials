package ai.hopsworks.tutorials.flink.tiktok.features;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.runtime.metrics.DescriptiveStatisticsHistogram;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

import java.time.Instant;

public class VideoEngagementProcessWindow
        extends ProcessWindowFunction<VideoWindowAggregationSchema, VideoWindowAggregationSchema, Long, TimeWindow> {


  private static final int EVENT_TIME_LAG_WINDOW_SIZE = 10_000;

  private transient DescriptiveStatisticsHistogram eventTimeLag;

  public VideoEngagementProcessWindow() {
  }

  @Override
  public void process(Long videoId, ProcessWindowFunction<VideoWindowAggregationSchema,
          VideoWindowAggregationSchema, Long, TimeWindow>.Context context,
                      Iterable<VideoWindowAggregationSchema> iterable,
                      Collector<VideoWindowAggregationSchema> collector) throws Exception {
    VideoWindowAggregationSchema record = iterable.iterator().next();

    // get process start timestamp
    Long processStart =  record.getWindowEndTime();

    record.setWindowEndTime(context.window().getEnd()  * 1000);

    // here it ends
    //eventTimeLag.update(Instant.now().toEpochMilli() - processStart);
    collector.collect(record);
  }

  @Override
  public void open(Configuration parameters) throws Exception {
    super.open(parameters);

    eventTimeLag =
            getRuntimeContext()
                    .getMetricGroup()
                    .histogram(
                            "videoEngagementEventTimeLag",
                            new DescriptiveStatisticsHistogram(EVENT_TIME_LAG_WINDOW_SIZE));
  }
}
