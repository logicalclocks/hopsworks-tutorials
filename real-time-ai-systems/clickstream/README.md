# Real-Time Clickstream Analytics - Pre-computed vs On-Demand

Comprehensive examples showing different approaches to real-time feature engineering with Hopsworks.

## Two Patterns, Same Goal

### 🚀 Pre-Computed Aggregations
Stream processing engines calculate features in real-time and store results.

```
Raw Events → Streaming Engine → Aggregated Features → Feature Store
                (Feldera/Flink)     (Ready to serve)
```

**Examples:**
- [CTR Calculation](./examples/ctr_calculation/) - Click-through rate with Feldera/Flink
- [Click Counts Pre-computed](./examples/click_counts/precomputed/) - Window aggregations with Feldera

### 🔄 On-Demand Aggregations
Store raw events, compute aggregations at query time.

```
Raw Events → Feature Store → Query-time Aggregation → Features
              (Raw storage)     (Compute on read)
```

**Example:**
- [Click Counts On-Demand](./examples/click_counts/on_demand/) - Spark batch + SQL aggregations

## Architecture Comparison

### Pre-Computed Pattern
```
1. Kafka Events (clickstream_events)
            ↓
2. Stream Processing (Feldera/Flink)
   - Window aggregations
   - Real-time computation
            ↓
3. Feature Group (aggregated)
   ├── RonDB (instant serving)
   └── Data Lake (historical)
            ↓
4. Feature View → get_feature_vector()
   Returns: Pre-computed values
```

### On-Demand Pattern (Future 4.7+)
```
1. Kafka Events (clickstream_events)
            ↓
2. Feature Group (raw events)
   ├── RonDB (stores raw)
   └── Data Lake (historical)
            ↓
3. Feature View with SQL
   SELECT COUNT(*) WHERE time > NOW() - INTERVAL 5 MIN
            ↓
4. get_feature_vector()
   Returns: Computed on-the-fly
```

## Performance Comparison

Based on Jim's benchmarks with 100k events:

| Pattern | Storage | Latency | Flexibility | Use Case |
|---------|---------|---------|-------------|----------|
| **Pre-computed** | Higher (stores all windows) | ~5ms per lookup | Fixed aggregations | High-frequency inference |
| **On-demand** | Lower (raw events only) | ~20-50ms per lookup | Dynamic queries | Exploratory, changing requirements |

## Examples Overview

### 1. CTR Calculation (Pre-computed)
Calculate click-through rate in real-time:
- **Metric**: CTR = clicks / impressions
- **Engines**: Feldera (SQL), Flink (Java)
- **Window**: 5-minute tumbling

### 2. Click Counts (Both Patterns)
Count user clicks over time windows:
- **Metric**: Click count per user
- **Windows**: 1, 10, 30, 60 minutes
- **Pre-computed**: Feldera with RANGE windows
- **On-demand**: Spark batch + MySQL queries

## Quick Start

### Pre-Computed Examples
```bash
# CTR with Feldera
cd examples/ctr_calculation/feldera
python setup.py
jupyter notebook 2_feldera_pipeline.ipynb

# Click counts with Feldera
cd examples/click_counts/precomputed
jupyter notebook 2a_feldera_pipeline.ipynb
```

### On-Demand Example
```bash
cd examples/click_counts/on_demand
jupyter notebook 3a_spark_batch.ipynb  # Store raw events
jupyter notebook 3b_online_inference.ipynb  # Query-time aggregation
```

## Trade-offs

### When to Pre-compute
✅ Known aggregations upfront
✅ Need <10ms latency
✅ High query volume
❌ Storage cost concerns
❌ Frequently changing requirements

### When to Use On-Demand
✅ Exploratory analytics
✅ Dynamic aggregations
✅ Storage efficiency
❌ Sub-10ms latency required
❌ Complex aggregations

## Future (v4.7+): Push-Down Aggregations

RonSQL will enable efficient on-demand aggregations directly in RonDB:

```python
# Future API (v4.7)
fv = fs.get_feature_view(
    query=clicks_fg.aggregate()
        .window("5 minutes")
        .group_by("user_id")
        .agg({"clicks": "count(*)"})
)

# Computed in RonDB, not application
features = fv.get_feature_vector({"user_id": "u123"})
```

## Repository Structure

```
clickstream/
├── examples/
│   ├── ctr_calculation/       # Pre-computed CTR
│   │   ├── feldera/           # SQL approach
│   │   └── flink/             # Java approach
│   └── click_counts/          # Click aggregations
│       ├── 1_synthetic_data.ipynb
│       ├── precomputed/       # Stream processing
│       └── on_demand/         # Query-time computation
└── README.md
```

## Key Takeaways

1. **Pre-computed**: Fast serving, fixed logic, higher storage
2. **On-demand**: Flexible queries, higher latency, efficient storage
3. **Hopsworks unifies both**: Same Feature Store, different patterns
4. **Choose based on requirements**: Latency vs flexibility trade-off

*Under the hood: Both patterns use Kafka for ingestion, but at different stages.*