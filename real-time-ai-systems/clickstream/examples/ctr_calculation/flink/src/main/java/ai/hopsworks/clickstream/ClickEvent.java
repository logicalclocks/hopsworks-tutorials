package ai.hopsworks.clickstream;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ClickEvent {
    @JsonProperty("user_id")
    private String userId;

    @JsonProperty("event_type")
    private String eventType;

    @JsonProperty("timestamp")
    private Long timestamp;

    // Default constructor for Jackson
    public ClickEvent() {}

    public ClickEvent(String userId, String eventType, Long timestamp) {
        this.userId = userId;
        this.eventType = eventType;
        this.timestamp = timestamp;
    }

    public String getUserId() {
        return userId;
    }

    public String getEventType() {
        return eventType;
    }

    public Long getTimestamp() {
        return timestamp;
    }

    public boolean isClick() {
        return "click".equals(eventType);
    }

    public boolean isImpression() {
        return "impression".equals(eventType);
    }
}