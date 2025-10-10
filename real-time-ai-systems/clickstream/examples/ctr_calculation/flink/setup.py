#!/usr/bin/env python
"""
Setup Kafka topics and feature groups for Flink CTR pipeline
"""

import hopsworks
import json
from hsfs.feature import Feature

# Connect to Hopsworks
project = hopsworks.login()
fs = project.get_feature_store()
kafka_api = project.get_kafka_api()

# Create Kafka topic for events
EVENTS_TOPIC = "clickstream_events"

events_schema = {
    "type": "record",
    "name": "clickstream_events_schema",
    "fields": [
        {"name": "user_id", "type": ["null", "string"]},
        {"name": "event_type", "type": ["null", "string"]},
        {"name": "timestamp", "type": ["null", "long"]}
    ]
}

if EVENTS_TOPIC not in [topic.name for topic in kafka_api.get_topics()]:
    kafka_api.create_schema("clickstream_events_schema", events_schema)
    kafka_api.create_topic(EVENTS_TOPIC, "clickstream_events_schema", 1, replicas=1, partitions=1)
    print(f"✅ Created Kafka topic: {EVENTS_TOPIC}")

# Create feature group for CTR
# Note: stream=True is implicit with Flink but we set it explicitly for clarity
# Hopsworks manages an internal Kafka topic transparently
ctr_fg = fs.get_or_create_feature_group(
    name="ctr_5min_flink",
    version=1,
    primary_key=["user_id"],
    event_time="window_end",
    online_enabled=True,
    stream=True,  # Explicit for clarity (automatic with Flink insertStream)
    features=[
        Feature("user_id", type="string"),
        Feature("impressions", type="bigint"),
        Feature("clicks", type="bigint"),
        Feature("ctr", type="double"),
        Feature("window_end", type="timestamp")
    ]
)

ctr_fg.save()
print(f"✅ Created feature group: ctr_5min_flink")
print(f"\n📝 Environment variables for Flink:")
print(f"   KAFKA_BOOTSTRAP_SERVERS={kafka_api.get_default_config()['bootstrap.servers']}")
print(f"   HOPSWORKS_HOST={project.host}")
print(f"   HOPSWORKS_PROJECT={project.name}")