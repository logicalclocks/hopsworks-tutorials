package ai.hopsworks.clickstream;

import java.time.Instant;

public class CTRAgg {
    private String userId;
    private Long impressions;
    private Long clicks;
    private Double ctr;
    private Instant windowEnd;

    public CTRAgg() {}

    public CTRAgg(String userId, Long impressions, Long clicks, Instant windowEnd) {
        this.userId = userId;
        this.impressions = impressions;
        this.clicks = clicks;
        this.ctr = impressions > 0 ? (double) clicks / impressions : 0.0;
        this.windowEnd = windowEnd;
    }

    public String getUserId() {
        return userId;
    }

    public Long getImpressions() {
        return impressions;
    }

    public Long getClicks() {
        return clicks;
    }

    public Double getCtr() {
        return ctr;
    }

    public Instant getWindowEnd() {
        return windowEnd;
    }
}