# Real-Time CTR with Flink (Java)

Production-ready Flink implementation with native Hopsworks integration.

## Setup

```bash
# 1. Create Kafka topics and feature groups
python setup.py

# 2. Build the JAR
mvn clean package
```

## Run

```bash
# Set environment variables (setup.py prints these)
export HOPSWORKS_HOST=your-host
export HOPSWORKS_PORT=443
export HOPSWORKS_PROJECT=your-project
export HOPSWORKS_API_KEY=your-api-key
export KAFKA_BOOTSTRAP_SERVERS=broker:9092

# Submit to Flink cluster
flink run target/clickstream-ctr-flink-1.0.jar
```

## Architecture

```
KafkaSource → Deserialize → Window(5min) → Aggregate → Hopsworks
```

### Key Components

- **ClickEvent**: POJO for Kafka events
- **CTRAccumulator**: Aggregates clicks/impressions
- **CTRWindowFunction**: Adds window timestamp
- **CTRAgg**: Output aggregation result

### Why Native Flink?

- **Zero overhead**: No Python ↔ JVM serialization
- **Type safety**: Compile-time checks
- **Performance**: 50-200ms latency vs 500ms+ for PyFlink
- **Production ready**: Battle-tested in enterprise

### Direct Hopsworks Integration

```java
StreamFeatureGroup featureGroup = fs.getStreamFeatureGroup("ctr_5min_flink", 1);
featureGroup.insertStream(ctrStream);
```

HSFS handles everything transparently:
- Internal Kafka topic (managed by Hopsworks)
- Serialization to Avro
- Online store writes (via OnlineFS service)
- Offline store sync (via Hudi DeltaStreamer)
- Schema validation

You don't manage Kafka - Hopsworks does it for you.