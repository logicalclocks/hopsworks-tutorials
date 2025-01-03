import hopsworks

project = hopsworks.login()

# create kafka topic
KAFKA_TOPIC_NAME = "live_interactions"
SCHEMA_NAME = "live_interactions_schema"

kafka_api = project.get_kafka_api()
job_api = project.get_jobs_api()

schema = {
    "type": "record",
    "name": SCHEMA_NAME,
    "namespace": "io.hops.examples.flink.examples",
    "fields": [
        {
            "name": "interaction_id",
            "type": [
                "null",
                "long"
            ]
        },
        {
            "name": "user_id",
            "type": [
                "null",
                "long"
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
            "name": "category_id",
            "type": [
                "null",
                "long"
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
        },
        {
            "name": "interaction_month",
            "type": [
                "null",
                "string"
            ]
        }
    ]
}

kafka_api.create_schema(SCHEMA_NAME, schema)
kafka_api.create_topic(KAFKA_TOPIC_NAME, SCHEMA_NAME, 1, replicas=1, partitions=20)
