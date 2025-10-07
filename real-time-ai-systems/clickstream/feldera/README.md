# Real-Time CTR with Feldera

```
Events → Kafka → Feldera (SQL) → Hopsworks
```

## SQL Pipeline

```sql
SELECT
  user_id,
  SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) as impressions,
  SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) as clicks,
  clicks / NULLIF(impressions, 0) as ctr,
  window_end
FROM TABLE(TUMBLE(TABLE events, DESCRIPTOR(timestamp), INTERVAL '5' MINUTES))
GROUP BY user_id, window_end;
```
