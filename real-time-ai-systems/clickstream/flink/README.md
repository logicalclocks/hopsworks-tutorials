# Real-Time CTR with Flink

```
Events → Kafka → Flink → Hopsworks
```

## PyFlink Pipeline

```python
# 5-minute window CTR calculation
SELECT
    user_id,
    COUNT(CASE WHEN event_type = 'impression' THEN 1 END) as impressions,
    COUNT(CASE WHEN event_type = 'click' THEN 1 END) as clicks,
    CAST(COUNT(CASE WHEN event_type = 'click' THEN 1 END) AS DOUBLE) /
        NULLIF(COUNT(CASE WHEN event_type = 'impression' THEN 1 END), 0) as ctr,
    TUMBLE_END(ts, INTERVAL '5' MINUTE) as window_end
FROM events
GROUP BY
    user_id,
    TUMBLE(ts, INTERVAL '5' MINUTE)
```