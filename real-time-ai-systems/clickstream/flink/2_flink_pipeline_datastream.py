#!/usr/bin/env python
"""
Flink DataStream API version (if you need UDFs or complex logic)
"""

import hopsworks
from pyflink.common import WatermarkStrategy, Duration
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer, KafkaSink, KafkaRecordSerializationSchema
from pyflink.datastream.functions import ProcessWindowFunction, AggregateFunction
from pyflink.datastream.window import TumblingEventTimeWindows, Time
import json
from datetime import datetime
from hsfs import engine

# Connect to Hopsworks
project = hopsworks.login()
fs = project.get_feature_store()
kafka_config = engine.get_instance()._get_kafka_config(fs.id, {})

EVENTS_TOPIC = "clickstream_events"
CTR_TOPIC = f"ctr_5min_{project.id}"

# Setup Flink
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

# Kafka source
source = KafkaSource.builder() \
    .set_bootstrap_servers(kafka_config['bootstrap.servers']) \
    .set_topics(EVENTS_TOPIC) \
    .set_group_id('flink_ctr_datastream') \
    .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

# Parse events
def parse_event(event_str):
    event = json.loads(event_str)
    return (
        event['user_id'],
        event['event_type'],
        event['timestamp']
    )

# CTR Aggregator
class CTRAggregator(AggregateFunction):
    def create_accumulator(self):
        return {'impressions': 0, 'clicks': 0}

    def add(self, value, accumulator):
        user_id, event_type, _ = value
        if event_type == 'impression':
            accumulator['impressions'] += 1
        elif event_type == 'click':
            accumulator['clicks'] += 1
        return accumulator

    def get_result(self, accumulator):
        return accumulator

    def merge(self, acc1, acc2):
        return {
            'impressions': acc1['impressions'] + acc2['impressions'],
            'clicks': acc1['clicks'] + acc2['clicks']
        }

# Window process function
class CTRWindowFunction(ProcessWindowFunction):
    def process(self, key, context, elements):
        stats = list(elements)[0]
        ctr = stats['clicks'] / stats['impressions'] if stats['impressions'] > 0 else 0.0

        result = {
            'user_id': key,
            'impressions': stats['impressions'],
            'clicks': stats['clicks'],
            'ctr': ctr,
            'window_end': datetime.fromtimestamp(context.window().end / 1000).isoformat()
        }

        yield json.dumps(result)

# Build pipeline
stream = env.from_source(source, WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(60)), "Kafka Source") \
    .map(parse_event) \
    .assign_timestamps_and_watermarks(
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(60))
        .with_timestamp_assigner(lambda event, _: event[2])
    ) \
    .key_by(lambda x: x[0]) \
    .window(TumblingEventTimeWindows.of(Time.minutes(5))) \
    .aggregate(
        CTRAggregator(),
        window_function=CTRWindowFunction(),
        output_type=Types.STRING()
    )

# Kafka sink
sink = KafkaSink.builder() \
    .set_bootstrap_servers(kafka_config['bootstrap.servers']) \
    .set_record_serializer(
        KafkaRecordSerializationSchema.builder()
        .set_topic(CTR_TOPIC)
        .set_value_serialization_schema(SimpleStringSchema())
        .build()
    ) \
    .build()

stream.sink_to(sink)

# Execute
env.execute("CTR Streaming Pipeline")