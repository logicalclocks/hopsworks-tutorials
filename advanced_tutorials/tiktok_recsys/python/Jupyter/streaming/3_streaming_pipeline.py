import json
from datetime import datetime, timedelta, timezone
import statistics

from bytewax.dataflow import Dataflow
from bytewax import operators as op
from bytewax.operators.window import EventClockConfig, TumblingWindow
from bytewax.connectors.kafka import operators as kop
import bytewax.operators.window as win
import hopsworks

from utils.hsfs_bytewax import get_kafka_config, serialize_with_key, sink_kafka
import config

def parse_value(msg):
    """Parse the JSON payload from a Kafka message into a Python dictionary."""
    return json.loads(msg.value.decode('utf-8'))

def get_event_time(event):
    """Retrieve and convert the event's datetime from the input to a timezone-aware datetime object."""
    return datetime.fromisoformat(event["interaction_date"]).replace(tzinfo=timezone.utc)

def accumulate(acc, event):
    """Accumulate watch times for each event to compute mean later."""
    acc.append(event["watch_time"])
    return acc

def format_event(event):
    """Calculate and format the aggregated results for output."""
    key, (metadata, data) = event
    mean_watch_time = statistics.mean(data) if data else 0
    return {
        "video_id": key,
        "week_start": metadata.start.isoformat(),
        "mean_watch_time": mean_watch_time,
        "interaction_count": len(data)
    }

def setup_dataflow(feature_group_name, feature_group_version, hopsworks_host, hopsworks_project, hopsworks_api_key):
    """Configure and return a Bytewax dataflow for aggregating video interaction data."""
    # Connect to hopsworks
    project = hopsworks.login(
        host=hopsworks_host,
        project=hopsworks_project,
        api_key_value=hopsworks_api_key
    )
    fs = project.get_feature_store()

    # Get feature group and its topic configuration
    feature_group = fs.get_feature_group(feature_group_name, feature_group_version)
    
    flow = Dataflow("video_interaction_aggregation")

    # Setup Kafka source
    kafka_config = get_kafka_config(feature_store_id=fs.id)
    stream = kop.input(
        "kafka_in", 
        flow, 
        brokers=[kafka_config['bootstrap.servers']], 
        topics=[config.KAFKA_TOPIC_NAME],
    )

    # Parse messages from Kafka
    parsed_stream = op.map("parse_value", stream.oks, parse_value)
    keyed_stream = op.key_on("key_on_video", parsed_stream, lambda e: e["video_id"])

    # Configure weekly windows
    clock = EventClockConfig(
        get_event_time, 
        wait_for_system_duration=timedelta(seconds=10),
    )
    week_window = TumblingWindow(
        length=timedelta(days=7),
        offset=timedelta(days=-datetime.utcnow().weekday()),
    )

    # Window aggregation for mean watch time
    windowed_stream = win.fold_window(
        "aggregate_watch_time", 
        keyed_stream, 
        clock, 
        week_window, 
        list, 
        accumulate,
    )
    formatted_stream = op.map(
        "format_event", 
        windowed_stream, 
        format_event,
    )

    # Output the formatted stream to another Kafka topic
    kop.output(
        "kafka_out", 
        formatted_stream, 
        brokers=[kafka_config['bootstrap.servers']], 
        topic=feature_group._online_topic_name, 
        add_config=kafka_config,
    )

    return flow

# Initialize and run the dataflow
if __name__ == "__main__":
    flow = setup_dataflow()
    flow.run()
