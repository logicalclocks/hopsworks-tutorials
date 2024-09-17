package ai.hopsworks.tutorials.flink.tiktok.utils;

public class TikTokInteractions {
    private Long interactionId;
    private Long userId;
    private Long videoId;
    private Long categoryId;
    private String interactionType;
    private Long watchTime;
    private Long interactionDate;
    private String interactionMonth;
    private Long processStart;


    public void setInteractionId(Long interactionId) {
        this.interactionId = interactionId;
    }

    public Long getInteractionId() {
        return interactionId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setVideoId(Long videoId) {
        this.videoId = videoId;
    }

    public Long getVideoId() {
        return videoId;
    }

    public void setCategoryId(Long categoryId) {
        this.categoryId = categoryId;
    }

    public Long getCategoryId() {
        return categoryId;
    }

    public void setInteractionType(String interactionType) {
        this.interactionType = interactionType;
    }

    public String getInteractionType() {
        return interactionType;
    }

    public void setWatchTime(Long watchTime) {
        this.watchTime = watchTime;
    }

    public Long getWatchTime() {
        return watchTime;
    }

    public void setInteractionDate(Long interactionDate) {
        this.interactionDate = interactionDate;
    }

    public Long getInteractionDate() {
        return interactionDate;
    }

    public void setInteractionMonth(String interactionMonth) {
        this.interactionMonth = interactionMonth;
    }

    public String getInteractionMonth() {
        return interactionMonth;
    }

    public void setProcessStart(Long processStart) {
        this.processStart = processStart;
    }

    public Long getProcessStart() {
        return processStart;
    }
}
