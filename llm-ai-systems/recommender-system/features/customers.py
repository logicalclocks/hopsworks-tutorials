import polars as pl
from enum import Enum
import random


class CustomerDatasetSize(Enum):
    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"

class DatasetSampler:
    _SIZES = {
        CustomerDatasetSize.LARGE: 50_000,
        CustomerDatasetSize.MEDIUM: 5_000,
        CustomerDatasetSize.SMALL: 1_000,
    }

    def __init__(self, size: CustomerDatasetSize) -> None:
        self._size = size

    @classmethod
    def get_supported_sizes(cls) -> dict:
        return cls._SIZES

    def sample(
        self, customers_df: pl.DataFrame, transations_df: pl.DataFrame
    ) -> dict[str, pl.DataFrame]:
        random.seed(27)

        n_customers = self._SIZES[self._size]
        print(f"✂️ Sampling {n_customers} customers.")
        customers_df = customers_df.sample(n=n_customers)

        print(f"⛳️ Number of transactions for all the customers: {transations_df.height}")
        transations_df = transations_df.join(
            customers_df.select("customer_id"), on="customer_id"
        )
        print(f"⛳️ Number of transactions for the {n_customers} sampled customers: {transations_df.height}")

        return {"customers": customers_df, "transactions": transations_df}


def fill_missing_club_member_status(df: pl.DataFrame) -> pl.DataFrame:
    """
    Fill missing values in the 'club_member_status' column with 'ABSENT'.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 'club_member_status' column.

    Returns:
    - pl.DataFrame: DataFrame with filled 'club_member_status' column.
    """
    return df.with_columns(pl.col("club_member_status").fill_null("ABSENT"))


def drop_na_age(df: pl.DataFrame) -> pl.DataFrame:
    """
    Drop rows with null values in the 'age' column.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 'age' column.

    Returns:
    - pl.DataFrame: DataFrame with rows containing null 'age' values removed.
    """
    return df.drop_nulls(subset=["age"])


def create_age_group() -> pl.Expr:
    """
    Create an expression to categorize age into groups.

    Returns:
    - pl.Expr: Polars expression that categorizes 'age' into predefined age groups.
    """
    return (
        pl.when(pl.col("age").is_between(0, 18))
        .then(pl.lit("0-18"))
        .when(pl.col("age").is_between(19, 25))
        .then(pl.lit("19-25"))
        .when(pl.col("age").is_between(26, 35))
        .then(pl.lit("26-35"))
        .when(pl.col("age").is_between(36, 45))
        .then(pl.lit("36-45"))
        .when(pl.col("age").is_between(46, 55))
        .then(pl.lit("46-55"))
        .when(pl.col("age").is_between(56, 65))
        .then(pl.lit("56-65"))
        .otherwise(pl.lit("66+"))
    ).alias("age_group")


def compute_features_customers(
    df: pl.DataFrame, drop_null_age: bool = False
) -> pl.DataFrame:
    """
    Prepare customer data by performing several data cleaning and transformation steps.

    This function does the following:
    1. Checks for required columns in the input DataFrame.
    2. Fills missing club member status with 'ABSENT'.
    3. Drops rows with missing age values.
    4. Creates an age group category.
    5. Casts the 'age' column to Float64.
    6. Selects and orders specific columns in the output.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing customer data.

    Returns:
    - pl.DataFrame: Processed DataFrame with cleaned and transformed customer data.

    Raises:
    - ValueError: If any of the required columns are missing from the input DataFrame.
    """
    required_columns = ["customer_id", "club_member_status", "age", "postal_code"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Columns {', '.join(missing_columns)} not found in the DataFrame"
        )

    df = (
        df.pipe(fill_missing_club_member_status)
        .pipe(drop_na_age)
        .with_columns([create_age_group(), pl.col("age").cast(pl.Float64)])
        .select(
            ["customer_id", "club_member_status", "age", "postal_code", "age_group"]
        )
    )

    if drop_null_age is True:
        df = df.drop_nulls(subset=["age"])

    return df
