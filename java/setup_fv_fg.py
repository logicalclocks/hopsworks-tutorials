import argparse

import numpy as np
import pandas as pd

import hopsworks
from hsfs.feature import Feature

def generate_data(size=1000, seed=42):
    """
    Generate a Pandas DataFrame with 400 columns of various types and random null values
    compatible with fastavro serialization

    Parameters:
    -----------
    size : int, optional (default=1000)
        Number of rows in the DataFrame
    seed : int, optional (default=42)
        Random seed for reproducibility

    Returns:
    --------
    pd.DataFrame
        Generated DataFrame with 400 mixed data types and null values
    """
    # Set random seed for reproducibility
    np.random.seed(seed)

    # Create a dictionary to store columns
    columns = {}

    # Create an empty helper function to create numeric columns with random nulls
    def create_numeric_column(generator, null_prob=0.1):
        """Create a column with random nulls using numpy"""
        values = generator(size)
        mask = np.random.random(size) < null_prob
        values[mask] = np.nan
        return values

    # Create an empty helper function for string columns
    def create_string_column(group_prefix, categories, null_prob=0.1):
        """Create a string column with random nulls"""
        values = [f"{group_prefix}_{np.random.randint(1, categories + 1)}" for _ in range(size)]
        mask = np.random.random(size) < null_prob
        for i in range(len(values)):
            if mask[i]:
                values[i] = None
        return values

    columns['id'] = [i for i in range(1000)]
    date_base = pd.date_range(end=pd.Timestamp.now(), periods=size)
    date_offsets = np.random.randint(0, 1500, size=size)
    timestamps = date_base - pd.to_timedelta(date_offsets, unit='D')
    columns['timestamp'] = [None if pd.isnull(ts) else ts for ts in timestamps]

    # Generate 400 columns with systematic naming and varied characteristics
    # Boolean-like Columns
    for i in range(20):
        columns[f'boolean_flag_{i + 1}'] = np.random.choice([True, False, None], size=size,
                                                            p=[0.45, 0.45, 0.1])

        # Byte-like Columns
        columns[f'byte_value_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(-128, 128, size=s).astype(float)
        )

        # Short Integer Columns
        columns[f'short_int_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(-32768, 32768, size=s).astype(float)
        )

        # Low Categorical Integer Columns
        columns[f'low_cat_int_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(1, 19, size=s).astype(float),
            null_prob=0.05
        )

        # High Categorical Integer Columns
        columns[f'high_cat_int_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(1, 200, size=s).astype(float),
            null_prob=0.15
        )

        # Long Columns (with some all-null)
        columns[f'long_col_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(-(2 ** 63), 2 ** 63 - 1, size=s).astype(float),
            null_prob=0.0
        )

        # Zero Standard Deviation Float Columns
        columns[f'float_zero_std_{i + 1}'] = create_numeric_column(
            lambda s: np.full(s, 100.0),
            null_prob=0.2
        )

        # Low Standard Deviation Float Columns
        columns[f'float_low_std_{i + 1}'] = create_numeric_column(
            lambda s: np.random.normal(100, 1.5, size=s),
            null_prob=0.1
        )

        # High Standard Deviation Float Columns
        columns[f'float_high_std_{i + 1}'] = create_numeric_column(
            lambda s: np.random.normal(100, 5.6, size=s),
            null_prob=0.15
        )

        # Double Columns
        columns[f'double_value_{i + 1}'] = create_numeric_column(
            lambda s: np.random.uniform(-1000, 1000, size=s),
            null_prob=0.1
        )

        # Decimal Columns
        columns[f'decimal_value_{i + 1}'] = create_numeric_column(
            lambda s: np.round(np.random.uniform(-1000, 1000, size=s), 2),
            null_prob=0.1
        )

        # Timestamp Columns
        date_offsets = np.random.randint(0, 1500, size=size)
        timestamps = date_base - pd.to_timedelta(date_offsets, unit='D')
        columns[f'timestamp_col_{i + 1}'] = [None if pd.isnull(ts) else ts for ts in timestamps]

        # Date Columns
        date_offsets = np.random.randint(0, 1500, size=size)
        dates = (date_base - pd.to_timedelta(date_offsets, unit='D')).date
        columns[f'date_{i + 1}'] = [None if pd.isnull(d) else d for d in dates]

        # Low Categorical String Columns
        columns[f'string_low_cat_{i + 1}'] = create_string_column(f'low_category', 19, null_prob=0.05)

        # High Categorical String Columns
        columns[f'string_high_cat_{i + 1}'] = create_string_column(f'high_category', 200, null_prob=0.15)

        # Array Columns
        columns[f'array_column_{i + 1}'] = [
            [np.random.randint(0, 10),
             np.random.randint(0, 100),
             np.random.randint(0, 1000)]
            for _ in range(size)
        ]

    columns[f'long_column_all_null'] = np.full(size, np.nan)
    # Create DataFrame in one go
    return pd.DataFrame(columns)


def connect(args):
    project = hopsworks.login(
        host=args.host, port=args.port, project=args.project, api_key_value=args.api_key
    )
    return project


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Hopsworks cluster configuration
    parser.add_argument("--host", help="Hopsworks cluster host")
    parser.add_argument(
        "--port", help="Port on which Hopsworks is listening on", default=443
    )
    parser.add_argument("--api_key", help="API key to authenticate with Hopsworks")
    parser.add_argument("--project", help="Name of the Hopsworks project to connect to")

    parser.add_argument("--feature_group_name", help="Name of the feature group")
    parser.add_argument("--feature_group_version", help="Version of the feature group")
    parser.add_argument("--feature_view_name", help="Name of the feature view")
    parser.add_argument("--feature_view_version", help="Version of the feature view")

    args = parser.parse_args()

    # Setup connection to Hopsworks
    project = connect(args)
    fs = project.get_feature_store()

    # Create FG for writing from Java client
    features = [
        Feature(name="id", type="int"),
        Feature(name="timestamp", type="timestamp"),
        Feature(name="boolean_flag", type="boolean"),
        Feature(name="byte_value", type="int"),
        Feature(name="short_int", type="int"),
        Feature(name="low_cat_int", type="int"),
        Feature(name="high_cat_int", type="int"),
        Feature(name="long_col", type="bigint"),
        Feature(name="float_zero_std", type="float"),
        Feature(name="float_low_std", type="float"),
        Feature(name="float_high_std", type="float"),
        Feature(name="double_value", type="double"),
        Feature(name="decimalValue", type="double"),
        Feature(name="timestamp_col", type="timestamp"),
        Feature(name="date_col", type="date"),
        Feature(name="string_low_cat", type="string"),
        Feature(name="string_high_cat", type="string"),
        Feature(name="array_column", type="array<int>"),
    ]

    fg = fs.create_feature_group(
        name="java_data",
        version=1,
        description="Feature Group for the Java POJO DataRow example",
        primary_key=["id"],
        event_time="timestamp",
        online_enabled=True,
        stream=True,
        statistics_config=False
    )

    # 4) Save feature metadata to Hopsworks
    if fg.id is None:
        fg.save(features)

    # create feature view for fetching using java client

    products_df = generate_data()
    products_fg = fs.get_or_create_feature_group(
        name="products",
        version=1,
        description="Products Data",
        primary_key=["id"],
        event_time="timestamp",
        stream=True,
        online_enabled=True,
    )
    products_fg.insert(products_df)

    products_fg = fs.get_feature_group(name="products", version=1)

    fs.get_or_create_feature_view(
        name='products_fv',
        version=1,
        query=products_fg.select_all(),
    )

