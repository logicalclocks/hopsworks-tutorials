# Real-Time CTR with Flink

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

## Components

- `ClickEvent.java` - Event POJO
- `CTRAccumulator.java` - Aggregates clicks/impressions
- `CTRWindowFunction.java` - Adds window timestamp
- `CTRAgg.java` - Output result

## Hopsworks Integration

```java
StreamFeatureGroup featureGroup = fs.getStreamFeatureGroup("ctr_5min_flink", 1);
featureGroup.insertStream(ctrStream);
```

Hopsworks manages the Kafka topic and storage.