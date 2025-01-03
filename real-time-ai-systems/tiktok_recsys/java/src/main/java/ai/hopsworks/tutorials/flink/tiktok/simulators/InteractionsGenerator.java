package ai.hopsworks.tutorials.flink.tiktok.simulators;

import ai.hopsworks.tutorials.flink.tiktok.utils.TikTokInteractions;
import org.apache.flink.api.connector.source.SourceReaderContext;
import org.apache.flink.connector.datagen.source.GeneratorFunction;

import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

public class InteractionsGenerator implements GeneratorFunction<Long, TikTokInteractions> {

    private final long maxInteractionId;

    private long interactionId = 0;

    private final Random randomNumber = new Random();

    private final List<String> interactionTypes = Arrays.asList("like", "view", "dislike", "comment", "share", "skip");
    private final List<Long> videoCategories = Arrays.asList(1L, 2L, 3L, 4L, 5L, 6L, 7L, 8L, 9L, 10L, 11L);

    SimpleDateFormat monthFormat = new SimpleDateFormat("yyyy-MM");

    Instant startTime;

    public InteractionsGenerator(long maxInteractionId, Instant startTime) {
        this.maxInteractionId = maxInteractionId;
        this.startTime = startTime;
    }

    @Override
    public void open(SourceReaderContext readerContext) throws Exception {
        GeneratorFunction.super.open(readerContext);
    }

    @Override
    public void close() throws Exception {
        GeneratorFunction.super.close();
    }

    @Override
    public TikTokInteractions map(Long aLong) throws Exception {
        return interactionEventGenerator(userIdGenerator(), videoIdGenerator(),
                videoCategoryTypeGenerator(), interactionTypeGenerator(),
                watchTimeGenerator());
    }

    private void interactionIdGenerator() {
        if (this.interactionId == this.maxInteractionId)  {
            this.interactionId = 0;
        } else {
            this.interactionId++;
        }
    }
    private Long userIdGenerator() {
        long leftLimit = 0L;
        long rightLimit = 100L;
        return leftLimit + (long) (Math.random() * (rightLimit - leftLimit));
    }

    private Long videoIdGenerator() {
        long leftLimit = 0L;
        long rightLimit = 100L;
        return leftLimit + (long) (Math.random() * (rightLimit - leftLimit));
    }

    private String interactionTypeGenerator() {
        return interactionTypes.get(randomNumber.nextInt(interactionTypes.size()));
    }

    private Long videoCategoryTypeGenerator() {
        return videoCategories.get(randomNumber.nextInt(interactionTypes.size()));
    }

    private Long watchTimeGenerator() {
        long leftLimit = 10L;
        long rightLimit = 250;
        return leftLimit + (long) (Math.random() * (rightLimit - leftLimit));
    }

    private void timestampGenerator(TikTokInteractions tikTokInteractions){
        //Long timestamp = Instant.now().toEpochMilli();
        this.startTime = this.startTime.plus(1, ChronoUnit.SECONDS);
        tikTokInteractions.setInteractionDate(startTime.toEpochMilli());
        tikTokInteractions.setInteractionMonth(this.monthFormat.format(startTime.toEpochMilli()));
    }

    private TikTokInteractions interactionEventGenerator(Long userId, Long videoId,Long videoCategory,
                                                         String interactionType,  Long watchTime) {

        interactionIdGenerator();

        TikTokInteractions tikTokInteractions = new TikTokInteractions();
        tikTokInteractions.setInteractionId(interactionId);
        tikTokInteractions.setUserId(userId);
        tikTokInteractions.setVideoId(videoId);
        tikTokInteractions.setCategoryId(videoCategory);
        tikTokInteractions.setInteractionType(interactionType);
        tikTokInteractions.setWatchTime(watchTime);
        timestampGenerator(tikTokInteractions);
        return tikTokInteractions;
    }
}
