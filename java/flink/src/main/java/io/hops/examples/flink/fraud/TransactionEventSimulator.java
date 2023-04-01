package io.hops.examples.flink.fraud;

import io.hops.examples.flink.examples.SourceTransaction;
import org.apache.flink.calcite.shaded.org.apache.commons.codec.digest.DigestUtils;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.api.watermark.Watermark;

import java.text.SimpleDateFormat;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class TransactionEventSimulator implements SourceFunction<SourceTransaction> {
  private final Random randTid = new Random();
  private final Random randAmount = new Random();
  
  private long eventTime;
  private String creditCardId;
  private SourceTransaction event;
  private int batch_size;
  
  public TransactionEventSimulator(int batch_size){
    this.batch_size = batch_size;
  }
  
  public static final int SLEEP_MILLIS_PER_EVENT = 5;
  private volatile boolean running = true;
  
  @Override
  public void run(SourceContext<SourceTransaction> sourceContext) throws Exception {
    long id = 0;
    long maxStartTime = 0;
    
    while (running) {
      // generate a batch of events
      List<SourceTransaction> events = new ArrayList<SourceTransaction>(batch_size);
      for (int i = 1; i <= batch_size; i++) {
        eventTime =  Instant.now().toEpochMilli();
        event = stringEventGenerator(tidGenerator(), ccNumGenerator(), amountGenerator(), eventTime);
        events.add(event);
      }
      
      events
        .iterator()
        .forEachRemaining(r -> sourceContext.collectWithTimestamp(event, eventTime));
      
      // produce a Watermark
      sourceContext.emitWatermark(new Watermark(maxStartTime));
      
      // prepare for the next batch
      id += batch_size;
      
      // don't go too fast
      Thread.sleep(SLEEP_MILLIS_PER_EVENT); //BATCH_SIZE * SLEEP_MILLIS_PER_EVENT
    }
  }
  
  @Override
  public void cancel() {
  }
  
  private long ccNumGenerator() {
    long leftLimit = 1L;
    long rightLimit = 1000L;
    return leftLimit + (long) (Math.random() * (rightLimit - leftLimit));
  }
  
  private String timestampGenerator(long timestamp){
    SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS");
    return dateFormat.format(timestamp);
  }
  
  private String tidGenerator() {
    int min = 1;
    int max = 10000;
    int ranfromNumber = randTid.nextInt(max - min) + min;
    return DigestUtils.sha256Hex("type" + ranfromNumber);
  }
  

  private double amountGenerator() {
    return randAmount.nextDouble();
  }
  
  private SourceTransaction stringEventGenerator(String eventId, long creditCardId, double amount, long eventTime) {
    SourceTransaction sourceTransaction = new SourceTransaction();
    sourceTransaction.setTid(eventId);
    sourceTransaction.setCcNum(creditCardId);
    sourceTransaction.setAmount(amount);
    sourceTransaction.setDatetime(eventTime);
    return sourceTransaction;
  }
}
