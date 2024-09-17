package ai.hopsworks.tutorials.flink.tiktok.features;

import ai.hopsworks.tutorials.flink.tiktok.utils.TikTokInteractions;
import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.runtime.metrics.DescriptiveStatisticsHistogram;

import java.time.Instant;

public class Interactions extends RichMapFunction<TikTokInteractions, SourceInteractions> {

    private static final int EVENT_TIME_LAG_WINDOW_SIZE = 10_000;

    private transient DescriptiveStatisticsHistogram eventTimeLag;

    @Override
    public SourceInteractions map(TikTokInteractions source) throws Exception {
        SourceInteractions interactionsFeatureGroupSchema = new SourceInteractions();
        interactionsFeatureGroupSchema.setId(source.getInteractionId());
        interactionsFeatureGroupSchema.setUserId(source.getUserId());
        interactionsFeatureGroupSchema.setVideoId(source.getVideoId());
        interactionsFeatureGroupSchema.setCategoryId(source.getCategoryId());
        interactionsFeatureGroupSchema.setInteractionType(source.getInteractionType());
        interactionsFeatureGroupSchema.setInteractionDate(source.getInteractionDate() * 1000);
        interactionsFeatureGroupSchema.setInteractionMonth(source.getInteractionMonth());
        interactionsFeatureGroupSchema.setWatchTime(source.getWatchTime());

        // update eventTimeLag
        eventTimeLag.update(Instant.now().toEpochMilli() - source.getProcessStart());

        return interactionsFeatureGroupSchema;
    }

    @Override
    public void open(Configuration parameters) throws Exception {
        super.open(parameters);

        eventTimeLag =
                getRuntimeContext()
                        .getMetricGroup()
                        .histogram(
                                "interactionsTimeLag",
                                new DescriptiveStatisticsHistogram(EVENT_TIME_LAG_WINDOW_SIZE));
    }
}
