import config
import hopsworks

# Login to Hopsworks project
project = hopsworks.login()

# Access Kafka API
kafka_api = project.get_kafka_api()

# Define the schema for Kafka messages
schema = {
    "type": "record",
    "name": config.SCHEMA_NAME,
    "namespace": "ai.hopsworks.examples.bytewax.interactions",
    "fields": [
        {
            "name": "interaction_id",
            "type": [
                "null",
                "string"
            ]
        },
        {
            "name": "user_id",
            "type": [
                "null",
                "string"
            ]
        },
        {
            "name": "video_id",
            "type": [
                "null",
                "string"
            ]
        },
        {
            "name": "interaction_type",
            "type": [
                "null",
                "string"
            ]
        },
        {
            "name": "watch_time",
            "type": [
                "null",
                "long"
            ]
        },
        {
            "name": "interaction_date",
            "type": [
                "null",
                {
                    "type": "long",
                    "logicalType": "timestamp-micros"
                }
            ]
        }
    ]
}

# Create schema in Hopsworks
kafka_api.create_schema(
    config.SCHEMA_NAME, 
    schema,
)

# Create Kafka topic
kafka_api.create_topic(
    config.KAFKA_TOPIC_NAME, 
    config.SCHEMA_NAME, 
    1,
    partitions=1, 
    replicas=1,
)
