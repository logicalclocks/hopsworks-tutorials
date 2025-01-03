from io import BytesIO
from hsfs import engine
from bytewax.connectors.kafka import KafkaSinkMessage

def _get_feature_group_config(feature_group):
    """
    fetches configuration for feature group online topic
    :param feature_group:
    :return:
    """

    if feature_group._kafka_producer is None:
        offline_write_options = {}  # {'internal_kafka': True}
        producer, feature_writers, writer = engine.get_instance()._init_kafka_resources(
            feature_group, offline_write_options
        )
        feature_group._kafka_producer = producer
        feature_group._feature_writers = feature_writers
        feature_group._writer = writer

    return feature_group


def serialize_with_key(key_payload, feature_group):
    key, row = key_payload

    feature_group = _get_feature_group_config(feature_group)

    # encode complex features
    row = engine.get_instance()._encode_complex_features(feature_group._feature_writers, row)

    # encode feature row
    with BytesIO() as outf:
        feature_group._writer(row, outf)
        encoded_row = outf.getvalue()

    # assemble key
    key = "".join([str(row[pk]) for pk in sorted(feature_group.primary_key)])

    return key, encoded_row


def sink_kafka(key, value, feature_group):  # -> KafkaSinkMessage[Dict, Dict]:

    # encode complex features
    headers = [
        ("projectId", str(feature_group.feature_store.project_id).encode("utf8")),
        ("featureGroupId", str(feature_group._id).encode("utf8")),
        ("subjectId", str(feature_group.subject["id"]).encode("utf8"))
    ]

    return KafkaSinkMessage(
        headers=headers,  # List[Tuple[str, bytes]] = field(default_factory=list)
        key=str({"identifier": key, "name": feature_group._online_topic_name}).encode('utf-8'),
        value=value,
    )


def get_kafka_config(feature_store_id):
    return engine.get_instance()._get_kafka_config(feature_store_id)
