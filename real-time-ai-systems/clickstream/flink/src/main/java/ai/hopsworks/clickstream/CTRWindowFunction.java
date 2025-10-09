package ai.hopsworks.clickstream;

import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

import java.time.Instant;

public class CTRWindowFunction extends ProcessWindowFunction<CTRAgg, CTRAgg, String, TimeWindow> {

    @Override
    public void process(String key,
                       Context context,
                       Iterable<CTRAgg> elements,
                       Collector<CTRAgg> out) {

        CTRAgg agg = elements.iterator().next();

        // Set the window end timestamp
        CTRAgg result = new CTRAgg(
            agg.getUserId(),
            agg.getImpressions(),
            agg.getClicks(),
            Instant.ofEpochMilli(context.window().getEnd())
        );

        out.collect(result);
    }
}