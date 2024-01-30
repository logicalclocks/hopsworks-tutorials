import hopsworks

project = hopsworks.login()

# create kafka topic
KAFKA_TOPIC_NAME = "credit_card_transactions"
SCHEMA_NAME = "credit_card_transactions_schema"

kafka_api = project.get_kafka_api()
job_api = project.get_jobs_api()

schema = {
    "type": "record",
    "name": SCHEMA_NAME,
    "namespace": "io.hops.examples.flink.examples",
    "fields": [{
        "name": "tid",
        "type": ["null", "string"]
    }, {
        "name": "datetime",
        "type": ["null", "long"]
    }, {
        "name": "cc_num",
        "type": ["null", "long"]
    }, {
        "name": "amount",
        "type": ["null", "double"]
    }]
}

kafka_api.create_schema(SCHEMA_NAME, schema)
kafka_api.create_topic(KAFKA_TOPIC_NAME, SCHEMA_NAME, 1, replicas=1, partitions=1)
