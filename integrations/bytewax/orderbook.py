import json

from io import BytesIO

from datetime import datetime, timezone
from websocket import create_connection

from bytewax.dataflow import Dataflow
from bytewax.inputs import PartitionedInput, StatefulSource
from bytewax.connectors.kafka import KafkaOutput

import hopsworks
from hsfs import engine


def get_feature_group_config(feature_group):
    """
    fetches configuration for feature group online topic
    :param feature_group:
    :return:
    """
    offline_write_options = {}
    fg_topic_config = engine.get_instance()._get_kafka_config(offline_write_options)

    _, feature_writers, writer = engine.get_instance()._init_kafka_resources(
        feature_group, offline_write_options
    )
    return fg_topic_config, feature_writers, writer


def serialize_with_key(key_payload, feature_group, feature_writers, writer):
    key, row = key_payload

    # encode complex features
    row = engine.get_instance()._encode_complex_features(feature_writers, row)

    # encode feature row
    with BytesIO() as outf:
        writer(row, outf)
        encoded_row = outf.getvalue()

    # assemble key
    key = "".join([str(row[pk]) for pk in sorted(feature_group.primary_key)])

    return key, encoded_row


class CoinfbaseSource(StatefulSource):
    def __init__(self, product_id):
        self.product_id = product_id
        self.ws = create_connection("wss://ws-feed.exchange.coinbase.com")
        self.ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": [product_id],
                    "channels": ["level2"],
                }
            )
        )
        # The first msg is just a confirmation that we have subscribed.
        print(self.ws.recv())

    def next(self):
        return self.ws.recv()

    def snapshot(self):
        return None

    def close(self):
        self.ws.close()


class CoinbaseFeedInput(PartitionedInput):
    def __init__(self, product_ids):
        self.product_ids = product_ids

    def list_parts(self):
        return set(self.product_ids)

    def build_part(self, for_key, resume_state):
        assert resume_state is None
        return CoinfbaseSource(for_key)


def key_on_product(data):
    return (data["product_id"], data)


class OrderBook:
    def __init__(self):
        # if using Python < 3.7 need to use OrderedDict here
        self.bids = {}
        self.asks = {}
        self.bid_price = None
        self.ask_price = None

    def update(self, data):
        if self.bids == {}:
            self.bids = {float(price): float(size) for price, size in data["bids"]}
            # The bid_price is the highest priced buy limit order.
            # since the bids are in order, the first item of our newly constructed bids
            # will have our bid price, so we can track the best bid
            self.bid_price = next(iter(self.bids))
        if self.asks == {}:
            self.asks = {float(price): float(size) for price, size in data["asks"]}
            # The ask price is the lowest priced sell limit order.
            # since the asks are in order, the first item of our newly constructed
            # asks will be our ask price, so we can track the best ask
            self.ask_price = next(iter(self.asks))
        else:
            # We receive a list of lists here, normally it is only one change,
            # but could be more than one.
            for update in data["changes"]:
                price = float(update[1])
                size = float(update[2])
            if update[0] == "sell":
                # first check if the size is zero and needs to be removed
                if size == 0.0:
                    try:
                        del self.asks[price]
                        # if it was the ask price removed,
                        # update with new ask price
                        if price <= self.ask_price:
                            self.ask_price = min(self.asks.keys())
                    except KeyError:
                        # don't need to add price with size zero
                        pass
                else:
                    self.asks[price] = size
                    if price < self.ask_price:
                        self.ask_price = price
            if update[0] == "buy":
                # first check if the size is zero and needs to be removed
                if size == 0.0:
                    try:
                        del self.bids[price]
                        # if it was the bid price removed,
                        # update with new bid price
                        if price >= self.bid_price:
                            self.bid_price = max(self.bids.keys())
                    except KeyError:
                        # don't need to add price with size zero
                        pass
                else:
                    self.bids[price] = size
                    if price > self.bid_price:
                        self.bid_price = price
        return self, {
            "ticker": data["product_id"],
            "timestamp": datetime.strptime("2023-07-17T18:03:25.947610Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                tzinfo=timezone.utc),
            "bid": self.bid_price,
            "bid_size": self.bids[self.bid_price],
            "ask": self.ask_price,
            "ask_price": self.asks[self.ask_price],
            "spread": self.ask_price - self.bid_price,
        }


def get_flow(feature_group_name, feature_group_version):
    flow = Dataflow()
    flow.input("input", CoinbaseFeedInput(["BTC-USD", "ETH-USD", "BTC-EUR", "ETH-EUR"]))
    flow.map(json.loads)
    # {
    #     'type': 'l2update',
    #     'product_id': 'BTC-USD',
    #     'changes': [['buy', '36905.39', '0.00334873']],
    #     'time': '2022-05-05T17:25:09.072519Z',
    # }
    flow.map(key_on_product)
    # ('BTC-USD', {
    #     'type': 'l2update',
    #     'product_id': 'BTC-USD',
    #     'changes': [['buy', '36905.39', '0.00334873']],
    #     'time': '2022-05-05T17:25:09.072519Z',
    # })
    flow.stateful_map("order_book", lambda: OrderBook(), OrderBook.update)
    # ('BTC-USD', (36905.39, 0.00334873, 36905.4, 1.6e-05, 0.010000000002037268))

    # get feature store handle
    project = hopsworks.login()
    fs = project.get_feature_store()

    # get feature group and its topic configuration
    feature_group = fs.get_feature_group(feature_group_name, feature_group_version)
    fg_topic_config, feature_writers, writer = get_feature_group_config(feature_group)

    # sync to feature group topic
    flow.map(lambda x: serialize_with_key(x, feature_group, feature_writers, writer))
    flow.output(
        "out",
        KafkaOutput(
            brokers=[fg_topic_config['bootstrap.servers']],
            topic=feature_group._online_topic_name,
            add_config=fg_topic_config
        )
    )
    return flow
