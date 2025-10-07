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

### [Flink](./flink/) - Most Flexible
```python
# Table API (SQL)
t_env.sql_query("SELECT ... FROM TUMBLE(...)")

# Or DataStream API for custom logic
class CTRAggregator(AggregateFunction):
    # Your Python UDF here
```
- **Lines of code**: 20-100
- **Latency**: 50-200ms (Java), 200-500ms (PyFlink)
- **When to use**: Need complex UDFs or stateful processing

### [PySpark](./pyspark/) - Best Integration
```python
df.groupBy(window("timestamp", "5 minutes"), "user_id") \
  .agg(sum(when(col("event_type") == "click", 1))) \
  .withColumn("ctr", col("clicks") / col("impressions"))
```
- **Lines of code**: 30
- **Latency**: 500ms-2s
- **When to use**: Already using Spark, need batch+stream

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

1. Pick an engine folder
2. Run `1_setup.ipynb` - Creates Kafka topics and feature groups
3. Run `2_*_pipeline.*` - Starts streaming pipeline
4. Run `3_read_features.ipynb` - Query your real-time features

## Why This Matters

**Without Hopsworks:** Different APIs, storage systems, and serving layers for each engine.

**With Hopsworks:** Same feature store, same serving API - regardless of engine.

You focus on your business logic. We handle the infrastructure.