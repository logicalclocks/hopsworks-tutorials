import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd
import numpy as np

def create_ffn(hidden_units: list, dropout_rate: float, name: str = None) -> keras.Sequential:
    """
    Create a feedforward neural network layer.

    Parameters:
    - hidden_units (list): List of integers specifying the number of units in each hidden layer.
    - dropout_rate (float): Dropout rate for regularization.
    - name (str): Name of the layer.

    Returns:
    keras.Sequential: Feedforward neural network layer.
    """
    fnn_layers = []

    for units in hidden_units:
        fnn_layers.append(layers.BatchNormalization())
        fnn_layers.append(layers.Dropout(dropout_rate))
        fnn_layers.append(layers.Dense(units, activation=tf.nn.gelu))

    return keras.Sequential(fnn_layers, name=name)

class GraphConvLayer(layers.Layer):
    """
    Graph Convolutional Layer.

    Parameters:
    - hidden_units (list): List of integers specifying the number of units in each hidden layer.
    - dropout_rate (float): Dropout rate for regularization.
    - aggregation_type (str): Type of aggregation for neighbor messages ('sum', 'mean', 'max').
    - combination_type (str): Type of combination for node embeddings ('gated', 'gru', 'concat', 'add').
    - normalize (bool): Flag to normalize node embeddings.
    """

    def __init__(
        self,
        hidden_units: list,
        dropout_rate: float = 0.2,
        aggregation_type: str = "mean",
        combination_type: str = "concat",
        normalize: bool = False,
        *args,
        **kwargs,
    ):
        super(GraphConvLayer, self).__init__(*args, **kwargs)

        self.aggregation_type = aggregation_type
        self.combination_type = combination_type
        self.normalize = normalize

        self.ffn_prepare = create_ffn(hidden_units, dropout_rate)
        if self.combination_type == "gated":
            self.update_fn = layers.GRU(
                units=hidden_units,
                activation="tanh",
                recurrent_activation="sigmoid",
                dropout=dropout_rate,
                return_state=True,
                recurrent_dropout=dropout_rate,
            )
        else:
            self.update_fn = create_ffn(hidden_units, dropout_rate)

    def prepare(self, node_repesentations, weights=None) -> tf.Tensor:
        """
        Prepare neighbor messages.

        Parameters:
        - node_repesentations (tf.Tensor): Node representations.
        - weights (tf.Tensor): Weights for neighbor messages.

        Returns:
        tf.Tensor: Prepared neighbor messages.
        """
        messages = self.ffn_prepare(node_repesentations)
        if weights is not None:
            messages = messages * tf.expand_dims(weights, -1)
        return messages

    def aggregate(self, node_indices, neighbour_messages) -> tf.Tensor:
        """
        Aggregate neighbor messages.

        Parameters:
        - node_indices (tf.Tensor): Node indices.
        - neighbour_messages (tf.Tensor): Neighbor messages.

        Returns:
        tf.Tensor: Aggregated messages.
        """
        num_nodes = tf.math.reduce_max(node_indices) + 1
        if self.aggregation_type == "sum":
            aggregated_message = tf.math.unsorted_segment_sum(
                neighbour_messages, node_indices, num_segments=num_nodes
            )
        elif self.aggregation_type == "mean":
            aggregated_message = tf.math.unsorted_segment_mean(
                neighbour_messages, node_indices, num_segments=num_nodes
            )
        elif self.aggregation_type == "max":
            aggregated_message = tf.math.unsorted_segment_max(
                neighbour_messages, node_indices, num_segments=num_nodes
            )
        else:
            raise ValueError(f"Invalid aggregation type: {self.aggregation_type}.")

        return aggregated_message

    def update(self, node_repesentations, aggregated_messages) -> tf.Tensor:
        """
        Update node embeddings.

        Parameters:
        - node_repesentations (tf.Tensor): Node representations.
        - aggregated_messages (tf.Tensor): Aggregated neighbor messages.

        Returns:
        tf.Tensor: Updated node embeddings.
        """
        if self.combination_type == "gru":
            h = tf.stack([node_repesentations, aggregated_messages], axis=1)
        elif self.combination_type == "concat":
            h = tf.concat([node_repesentations, aggregated_messages], axis=1)
        elif self.combination_type == "add":
            h = node_repesentations + aggregated_messages
        else:
            raise ValueError(f"Invalid combination type: {self.combination_type}.")

        node_embeddings = self.update_fn(h)
        if self.combination_type == "gru":
            node_embeddings = tf.unstack(node_embeddings, axis=1)[-1]

        if self.normalize:
            node_embeddings = tf.nn.l2_normalize(node_embeddings, axis=-1)
        return node_embeddings

    def call(self, inputs) -> tf.Tensor:
        """
        Process inputs to produce node embeddings.

        Parameters:
        inputs: a tuple of three elements: node_repesentations, edges, edge_weights.

        Returns:
        tf.Tensor: Node embeddings.
        """
        node_repesentations, edges, edge_weights = inputs
        node_indices, neighbour_indices = edges[0], edges[1]
        neighbour_repesentations = tf.gather(node_repesentations, neighbour_indices)

        neighbour_messages = self.prepare(neighbour_repesentations, edge_weights)
        aggregated_messages = self.aggregate(node_indices, neighbour_messages)
        return self.update(node_repesentations, aggregated_messages)


class GNNNodeClassifier(tf.keras.Model):
    """
    Graph Neural Network Node Classifier.

    Parameters:
    - graph_info: Tuple of node_features, edges, and edge_weights.
    - hidden_units (list): List of integers specifying the number of units in each hidden layer.
    - aggregation_type (str): Type of aggregation for neighbor messages ('sum', 'mean', 'max').
    - combination_type (str): Type of combination for node embeddings ('gated', 'gru', 'concat', 'add').
    - dropout_rate (float): Dropout rate for regularization.
    - normalize (bool): Flag to normalize node embeddings.
    """

    def __init__(
        self,
        graph_info: tuple,
        hidden_units: list,
        aggregation_type: str = "sum",
        combination_type: str = "concat",
        dropout_rate: float = 0.2,
        normalize: bool = True,
        *args,
        **kwargs,
    ):
        super(GNNNodeClassifier, self).__init__(*args, **kwargs)

        node_features, edges, edge_weights = graph_info
        self.node_features = node_features
        self.edges = edges
        self.edge_weights = edge_weights

        if self.edge_weights is None:
            self.edge_weights = tf.ones(shape=edges.shape[1])

        self.edge_weights = self.edge_weights / tf.math.reduce_sum(self.edge_weights)

        self.preprocess = create_ffn(hidden_units, dropout_rate, name="preprocess")
        self.conv1 = GraphConvLayer(
            hidden_units,
            dropout_rate,
            aggregation_type,
            combination_type,
            normalize,
            name="graph_conv1",
        )
        self.conv2 = GraphConvLayer(
            hidden_units,
            dropout_rate,
            aggregation_type,
            combination_type,
            normalize,
            name="graph_conv2",
        )
        self.postprocess = create_ffn(hidden_units, dropout_rate, name="postprocess")
        self.compute_logits = layers.Dense(hidden_units[0], activation=tf.nn.tanh, name="logits")

    def call(self, input_node_indices) -> tf.Tensor:
        """
        Make predictions.

        Parameters:
        - input_node_indices (tf.Tensor): Input node indices.

        Returns:
        tf.Tensor: Predictions.
        """
        x = self.preprocess(self.node_features)
        x1 = self.conv1((x, self.edges, self.edge_weights))
        x = x1 + x
        x2 = self.conv2((x, self.edges, self.edge_weights))
        x = x2 + x
        x = self.postprocess(x)
        node_embeddings = tf.gather(x, input_node_indices)
        return self.compute_logits(node_embeddings)


def construct_graph(input_df: pd.DataFrame, data_party_labels: pd.DataFrame) -> dict:
    """
    Construct a graph and generate node embeddings.

    Parameters:
    - input_df (pd.DataFrame): Input transaction DataFrame.
    - data_party_labels (pd.DataFrame): DataFrame containing party labels.

    Returns:
    dict: Dictionary with keys 'id' and 'graph_embeddings'.
    """
    sampled_party = data_party_labels[data_party_labels.id.isin(input_df.source) | (data_party_labels.id.isin(input_df.target))]
    sampled_party = sampled_party[["id", "type", "is_sar"]]

    unique_ids = set(sampled_party.id.values)
    id_dict = {idn: i for i, idn in enumerate(unique_ids)}

    sampled_party['int_id'] = sampled_party['id'].apply(lambda x: id_dict[x])
    input_df['source'] = input_df['source'].apply(lambda x: id_dict[x])
    input_df['target'] = input_df['target'].apply(lambda x: id_dict[x])

    feature_names = ["type"]
    x_train = sampled_party.int_id.to_numpy()

    edges = input_df[["source", "target"]].to_numpy().T
    edge_weights = tf.ones(shape=edges.shape[1])
    node_features = tf.cast(
        sampled_party.sort_values("id")[feature_names].to_numpy(), dtype=tf.dtypes.float32
    )
    graph_info = (node_features, edges, edge_weights)

    # Hyperparameters for graph embeddings model
    hidden_units = [32, 32]
    learning_rate = 0.01
    dropout_rate = 0.5
    num_epochs = 2
    batch_size = 256

    # Construct the model
    model = GNNNodeClassifier(
        graph_info=graph_info,
        hidden_units=hidden_units,
        dropout_rate=dropout_rate,
        name="gnn_model",
    )

    # Compile the model.
    model.compile(
        optimizer=keras.optimizers.RMSprop(learning_rate=learning_rate),
        loss=keras.losses.MeanSquaredError(),
        metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")],
    )

    # Fit the model.
    history = model.fit(
        x=x_train,
        y=x_train,
        epochs=num_epochs,
        batch_size=batch_size,
    )

    graph_embeddings = list(model.predict(x_train).reshape(node_features.shape[0], hidden_units[0]))
    return {"id": sampled_party.id.to_numpy(), "graph_embeddings": graph_embeddings}
