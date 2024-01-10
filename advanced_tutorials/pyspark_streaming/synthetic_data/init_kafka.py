import hopsworks

# create kafka topic
KAFKA_TOPIC_NAME = "credit_card_transactions"
SCHEMA_NAME = "credit_card_transactions_schema"

schema = {
    "type": "record",
    "name": SCHEMA_NAME,
    "namespace": "io.hops.examples.flink.examples",
    "fields": [
        {
            "name": "tid",
            "type": [
                "null",
                "string"
            ]
        },
        {
            "name": "datetime",
            "type": [
                "null",
                {
                    "type": "long",
                    "logicalType": "timestamp-micros"
                }
            ]
        },
        {
            "name": "cc_num",
            "type": [
                "null",
                "long"
            ]
        },
        {
            "name": "category",
            "type": [
                "null",
                "string"
            ]
        },
        {
            "name": "amount",
            "type": [
                "null",
                "double"
            ]
        },
        {
            "name": "latitude",
            "type": [
                "null",
                "double"
            ]
        },
        {
            "name": "longitude",
            "type": [
                "null",
                "double"
            ]
        },
        {
            "name": "city",
            "type": [
                "null",
                "string"
            ]
        },
        {
            "name": "country",
            "type": [
                "null",
                "string"
            ]
        },
    ]
}

def init():
    project = hopsworks.login()
    kafka_api = project.get_kafka_api()
    kafka_api.create_schema(SCHEMA_NAME, schema)
    kafka_api.create_topic(KAFKA_TOPIC_NAME, SCHEMA_NAME, 1, replicas=1, partitions=1)
