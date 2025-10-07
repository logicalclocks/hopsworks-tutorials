# Real-Time CTR with PySpark

```
Events → Kafka → PySpark Streaming → Hopsworks
```

## PySpark Pipeline

```python
# 5-minute window CTR calculation
df = spark \
    .readStream \
    .format("kafka") \
    .load() \
    .groupBy(
        window("timestamp", "5 minutes"),
        "user_id"
    ) \
    .agg(
        sum(when(col("event_type") == "impression", 1).otherwise(0)).alias("impressions"),
        sum(when(col("event_type") == "click", 1).otherwise(0)).alias("clicks")
    ) \
    .withColumn("ctr", col("clicks") / when(col("impressions") > 0, col("impressions")).otherwise(lit(None)))
```