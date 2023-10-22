"""Connectors for [Kafka](https://kafka.apache.org).

Importing this module requires the
[`confluent-kafka`](https://github.com/confluentinc/confluent-kafka-python)
package to be installed.

"""
from io import BytesIO

from bytewax.outputs import DynamicOutput, StatelessSink
from hsfs import engine

__all__ = [
    "KafkaOutput",
]


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


def _list_parts(client, topics):
    for topic in topics:
        # List topics one-by-one so if auto-create is turned on,
        # we respect that.
        cluster_metadata = client.list_topics(topic)
        topic_metadata = cluster_metadata.topics[topic]
        if topic_metadata.error is not None:
            msg = (
                f"error listing partitions for Kafka topic `{topic!r}`: "
                f"{topic_metadata.error.str()}"
            )
            raise RuntimeError(msg)
        part_idxs = topic_metadata.partitions.keys()
        for i in part_idxs:
            yield f"{i}-{topic}"


class _KafkaSink(StatelessSink):
    def __init__(self, feature_group):
        self._feature_group = feature_group
        self._producer = feature_group._kafka_producer
        self._topic = feature_group._online_topic_name

    def write_batch(self, batch):
        for key, value in batch:
            self._producer.produce(self._topic, value, key,
                                   headers={
                                       "projectId": str(self._feature_group.feature_store.project_id).encode(
                                           "utf8"
                                       ),
                                       "featureGroupId": str(self._feature_group._id).encode("utf8"),
                                       "subjectId": str(self._feature_group.subject["id"]).encode("utf8"),
                                   }
                                )
            self._producer.poll(0)
        self._producer.flush()

    def close(self):
        self._producer.flush()


class KafkaOutput(DynamicOutput):
    """Use a single Kafka topic as an output sink.

    Items consumed from the dataflow must look like two-tuples of
    `(key_bytes, value_bytes)`. Default partition routing is used.

    Workers are the unit of parallelism.

    Can support at-least-once processing. Messages from the resume
    epoch will be duplicated right after resume.

    """

    def __init__(
            self,
            feature_group,
    ):
        """Init.
        Args:
            feature_group:
                feature_group to write to.
        """
        self._feature_group = _get_feature_group_config(feature_group)

    def build(self, worker_index, worker_count):
        """See ABC docstring."""
        return _KafkaSink(self._feature_group)
