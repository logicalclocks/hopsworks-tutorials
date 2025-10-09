# Real-Time CTR Calculation - Choose Your Engine

Same use case, multiple streaming engines. **Hopsworks handles the complexity, you pick the tool.**

## The Use Case
Calculate Click-Through Rate (CTR) in real-time:
- 5-minute tumbling windows
- Group by user
- CTR = clicks / impressions

## Data Flow Architecture

### Both Engines Follow Same Pattern
```
1. Raw Events (e.g., clickstream_events)
            ↓
2. Stream Processing Engine
   - Feldera: SQL with TUMBLE windows
   - Flink: DataStream API with CTRAccumulator
            ↓
3. Write to Feature Group
   - Feldera: Via Kafka topic (explicit)
   - Flink: Via insertStream() API
            ↓
4. Hopsworks Feature Store*
   ├── RonDB (real-time serving)
   └── Data Lake (batch job for historical)
            ↓
5. Feature View → get_feature_vector() → ML Model
```

*Under the hood: Hopsworks uses Kafka for reliable ingestion, but this is transparent to you.

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

Regardless of engine, Hopsworks provides:

```python
# 1. Feature Group (stores computed features)
fg = fs.get_or_create_feature_group(
    name="ctr_5min",
    stream=True,           # ← Enable streaming ingestion
    online_enabled=True    # ← Enable real-time serving
)

# 2. Feature View (serves features)
fv = fs.get_or_create_feature_view(
    name="ctr_fv",
    query=fg.select_all()
)

# 3. Real-time lookup (same API for all engines)
features = fv.get_feature_vector({"user_id": "user_123"})
# → {"impressions": 100, "clicks": 5, "ctr": 0.05}
```

**What Hopsworks handles:**
- Kafka → Feature Store synchronization
- Dual storage: Online (RonDB) + Offline (Hudi)
- Schema management and validation
- Exactly-once semantics via idempotent writes

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