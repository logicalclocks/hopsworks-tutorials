# Real-Time CTR Calculation - Choose Your Engine

Same use case, multiple streaming engines. **Hopsworks handles the complexity, you pick the tool.**

## The Use Case
Calculate Click-Through Rate (CTR) in real-time:
- 5-minute tumbling windows
- Group by user
- CTR = clicks / impressions

## Pick Your Engine

### [Feldera](./feldera/) - Simplest
```sql
SELECT user_id,
       SUM(clicks) / NULLIF(SUM(impressions), 0) as ctr
FROM TUMBLE(events, DESCRIPTOR(timestamp), INTERVAL '5' MINUTES)
GROUP BY user_id, window_end
```
- **Lines of code**: 12
- **Latency**: 10-50ms
- **When to use**: You want simple SQL, lowest latency

### [Flink](./flink/) - Production Ready
```java
// Native Java implementation
events
    .keyBy(ClickEvent::getUserId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new CTRAccumulator(), new CTRWindowFunction());
```
- **Lines of code**: ~100 (Java boilerplate)
- **Latency**: 50-200ms
- **When to use**: Production workloads, need guaranteed processing

## The Magic: Hopsworks Unifies Everything

All engines write to Hopsworks the same way:

```python
# Create streaming feature group
fg = fs.get_or_create_feature_group(
    name="ctr_5min",
    stream=True,           # ← Enable streaming
    online_enabled=True,   # ← Real-time serving
    topic_name=KAFKA_TOPIC # ← Auto-ingestion from Kafka
)

# That's it. Hopsworks handles:
# - Kafka → Feature Store ingestion
# - Online store (low-latency serving)
# - Offline store (via materialization jobs)
# - Schema management
```

## Quick Start

### Feldera
1. Run `1_setup.ipynb` - Creates Kafka topics and feature groups
2. Run `2_feldera_pipeline.ipynb` - Starts SQL streaming
3. Run `3_read_features.ipynb` - Query features

### Flink (Java)
1. `mvn clean package` - Build the JAR
2. Set environment variables (see flink/README.md)
3. `flink run target/clickstream-ctr-flink-1.0.jar`
4. Query features via Hopsworks UI or API

## Why This Matters

**Without Hopsworks:** Different APIs, storage systems, and serving layers for each engine.

**With Hopsworks:** Same feature store, same serving API - regardless of engine.

You focus on your business logic. We handle the infrastructure.