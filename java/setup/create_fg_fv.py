### <span style='color:#ff5f27'> 📝 Imports

import dbldatagen as dg
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, FloatType, StringType, BooleanType, TimestampType, ArrayType
from pyspark.sql.functions import pandas_udf

import pandas as pd
import numpy as np

import hopsworks
import random

### <span style='color:#ff5f27'> 👩🏻‍🔬 Generation Function
spark = SparkSession.builder.enableHiveSupport().getOrCreate()


def generate_data(n_rows):
    df_spec = (
        dg.DataGenerator(spark, name="Products_Data", rows=n_rows, partitions=4)
            .withColumn(
            "user_id",
            IntegerType(),
            minValue=0,
            maxValue=300000,
            random=True,
        )
            .withColumn(
            "product_id",
            IntegerType(),
            minValue=0,
            maxValue=1000,
            random=True,
        )
            .withColumn(
            "timestamp",
            TimestampType(),
            random=True,
        )
            .withColumn(
            "col_float",
            FloatType(),
            expr="floor(rand() * 350) * (86400 + 3600)",
            numColumns=110,
            random=True,
        )
            .withColumn(
            "col_str",
            StringType(),
            numColumns=8,
            values=['a', 'b', 'c', 'd', 'e', 'f', 'g'],
            random=True,

        )
            .withColumn(
            "col_int",
            IntegerType(),
            numColumns=6,
            minValue=0,
            maxValue=500,
            random=True,
        )
            .withColumn(
            "col_bool",
            BooleanType(),
            numColumns=4,
            random=True,
        )
    )

    df = df_spec.build()

    return df


@pandas_udf(ArrayType(IntegerType()))
def generate_list_col(rows: pd.Series) -> pd.Series:
    return pd.Series([np.random.randint(100, size=random.randint(10, 31)) for _ in range(len(rows))])

@pandas_udf(ArrayType(IntegerType()))
def generate_click_col(rows: pd.Series) -> pd.Series:
    return pd.Series([np.random.randint(10, size=random.randint(0, 5)) for _ in range(len(rows))])

## <span style="color:#ff5f27;">🔮 Generate Data </span>
n_rows = 5_000

data_generated_products = generate_data(n_rows)

# Get the number of rows
num_rows = data_generated_products.count()

# Get the number of columns
num_columns = len(data_generated_products.columns)

print("Number of rows:", num_rows)
print("Number of columns:", num_columns)

for i in range(6):
    data_generated_products = data_generated_products.withColumn(
        f'col_list_{i}',
        generate_list_col(data_generated_products.product_id + i)
    )

data_generated_products = data_generated_products.withColumn("clicks", generate_click_col(data_generated_products.product_id + i))

clicks_df = data_generated_products.select("user_id", "product_id", "timestamp", "clicks")
products_df = data_generated_products.drop("user_id", "clicks")

# Get the number of rows
num_rows = data_generated_products.count()

# Get the number of columns
num_columns = len(data_generated_products.columns)

print("Number of rows:", num_rows)
print("Number of columns:", num_columns)

## <span style="color:#ff5f27;">🪄 Feature Group Creation</span>
project = hopsworks.login()
fs = project.get_feature_store()

products_fg = fs.get_or_create_feature_group(
    name="products",
    version=1,
    description="Products Data",
    primary_key=["product_id"],
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
