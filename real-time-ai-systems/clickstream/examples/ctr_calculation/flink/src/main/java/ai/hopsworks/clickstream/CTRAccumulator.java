package ai.hopsworks.clickstream;

import org.apache.flink.api.common.functions.AggregateFunction;

public class CTRAccumulator implements AggregateFunction<ClickEvent, CTRAccumulator.CTRState, CTRAgg> {

    public static class CTRState {
        public String userId = "";
        public long impressions = 0;
        public long clicks = 0;
    }

    @Override
    public CTRState createAccumulator() {
        return new CTRState();
    }

    @Override
    public CTRState add(ClickEvent event, CTRState state) {
        state.userId = event.getUserId();

        if (event.isImpression()) {
            state.impressions++;
        } else if (event.isClick()) {
            state.clicks++;
        }

        return state;
    }

    @Override
    public CTRAgg getResult(CTRState state) {
        return new CTRAgg(
            state.userId,
            state.impressions,
            state.clicks,
            null  // Window end will be set by ProcessWindowFunction
        );
    }

    @Override
    public CTRState merge(CTRState a, CTRState b) {
        CTRState merged = new CTRState();
        merged.userId = a.userId;
        merged.impressions = a.impressions + b.impressions;
        merged.clicks = a.clicks + b.clicks;
        return merged;
    }
}