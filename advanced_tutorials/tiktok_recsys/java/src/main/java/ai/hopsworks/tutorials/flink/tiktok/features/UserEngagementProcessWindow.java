package ai.hopsworks.tutorials.flink.tiktok.features;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.runtime.metrics.DescriptiveStatisticsHistogram;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

import java.time.Instant;

public class UserEngagementProcessWindow extends ProcessWindowFunction<UserWindowAggregationSchema, UserWindowAggregationSchema, Long, TimeWindow> {

  private static final int EVENT_TIME_LAG_WINDOW_SIZE = 10_000;

  private transient DescriptiveStatisticsHistogram eventTimeLag;

  @Override
  public void process(Long userId, ProcessWindowFunction<UserWindowAggregationSchema, UserWindowAggregationSchema,
          Long, TimeWindow>.Context context, Iterable<UserWindowAggregationSchema> iterable, Collector<UserWindowAggregationSchema> collector) {

    UserWindowAggregationSchema record = iterable.iterator().next();

    // get process start timestamp
    Long processStart =  record.getWindowEndTime();

    // window end
    record.setWindowEndTime(context.window().getEnd()  * 1000);

    // here it ends
    collector.collect(record);

    // measure latency
    //eventTimeLag.update(Instant.now().toEpochMilli() - processStart);
  }

  @Override
  public void open(Configuration parameters) throws Exception {
    super.open(parameters);

    eventTimeLag =
            getRuntimeContext()
                    .getMetricGroup()
                    .histogram(
                            "userEngagementEventTimeLag",
                            new DescriptiveStatisticsHistogram(EVENT_TIME_LAG_WINDOW_SIZE));
  }
}
