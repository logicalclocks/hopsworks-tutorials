### <span style='color:#ff5f27'> 📝 Imports

import numpy as np
import pandas as pd

import hopsworks


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
    for i in range(20):
        columns[f'byte_value_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(-128, 128, size=s).astype(float)
        )

    # Short Integer Columns
    for i in range(20):
        columns[f'short_int_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(-32768, 32768, size=s).astype(float)
        )

    # Low Categorical Integer Columns
    for i in range(20):
        columns[f'low_cat_int_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(1, 19, size=s).astype(float),
            null_prob=0.05
        )

    # High Categorical Integer Columns
    for i in range(20):
        columns[f'high_cat_int_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(1, 200, size=s).astype(float),
            null_prob=0.15
        )

    # Long Columns (with some all-null)
    for i in range(19):
        columns[f'long_col_{i + 1}'] = create_numeric_column(
            lambda s: np.random.randint(-(2 ** 63), 2 ** 63 - 1, size=s).astype(float),
            null_prob=0.0
        )
    columns[f'long_column_all_null'] = np.full(size, np.nan)

    # Zero Standard Deviation Float Columns
    for i in range(20):
        columns[f'float_zero_std_{i + 1}'] = create_numeric_column(
            lambda s: np.full(s, 100.0),
            null_prob=0.2
        )

    # Low Standard Deviation Float Columns
    for i in range(20):
        columns[f'float_low_std_{i + 1}'] = create_numeric_column(
            lambda s: np.random.normal(100, 1.5, size=s),
            null_prob=0.1
        )

    # High Standard Deviation Float Columns
    for i in range(20):
        columns[f'float_high_std_{i + 1}'] = create_numeric_column(
            lambda s: np.random.normal(100, 5.6, size=s),
            null_prob=0.15
        )

    # Double Columns
    for i in range(20):
        columns[f'double_value_{i + 1}'] = create_numeric_column(
            lambda s: np.random.uniform(-1000, 1000, size=s),
            null_prob=0.1
        )

    # Decimal Columns
    for i in range(20):
        columns[f'decimal_value_{i + 1}'] = create_numeric_column(
            lambda s: np.round(np.random.uniform(-1000, 1000, size=s), 2),
            null_prob=0.1
        )

    # Timestamp Columns
    date_base = pd.date_range(end=pd.Timestamp.now(), periods=size)
    for i in range(20):
        date_offsets = np.random.randint(0, 1500, size=size)
        timestamps = date_base - pd.to_timedelta(date_offsets, unit='D')
        columns[f'timestamp_col_{i + 1}'] = [None if pd.isnull(ts) else ts for ts in timestamps]

    # Date Columns
    for i in range(20):
        date_offsets = np.random.randint(0, 1500, size=size)
        dates = (date_base - pd.to_timedelta(date_offsets, unit='D')).date
        columns[f'date_{i + 1}'] = [None if pd.isnull(d) else d for d in dates]

    # Low Categorical String Columns
    for i in range(20):
        columns[f'string_low_cat_{i + 1}'] = create_string_column(f'low_category', 19, null_prob=0.05)

    # High Categorical String Columns
    for i in range(20):
        columns[f'string_high_cat_{i + 1}'] = create_string_column(f'high_category', 200, null_prob=0.15)

    # Array Columns
    for i in range(20):
        columns[f'array_column_{i + 1}'] = [
            [np.random.randint(0, 10),
             np.random.randint(0, 100),
             np.random.randint(0, 1000)]
            for _ in range(size)
        ]

    # Create DataFrame in one go
    return pd.DataFrame(columns)


products_df = generate_data()

## <span style="color:#ff5f27;">🪄 Feature Group Creation</span>
project = hopsworks.login()
fs = project.get_feature_store()

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
