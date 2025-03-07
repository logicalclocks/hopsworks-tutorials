import numpy as np
import pandas as pd
import polars as pl
from hopsworks import udf


def convert_article_id_to_str(df: pl.DataFrame) -> pl.Series:
    """
    Convert the 'article_id' column to string type.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 'article_id' column.

    Returns:
    - pl.Series: The 'article_id' column converted to string type.
    """
    return df["article_id"].cast(pl.Utf8)


def convert_t_dat_to_datetime(df: pl.DataFrame) -> pl.Series:
    """
    Convert the 't_dat' column to datetime type.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pl.Series: The 't_dat' column converted to datetime type.
    """
    return pl.from_pandas(pd.to_datetime(df["t_dat"].to_pandas()))


def get_year_feature(df: pl.DataFrame) -> pl.Series:
    """
    Extract the year from the 't_dat' column.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pl.Series: A series containing the year extracted from 't_dat'.
    """
    return df["t_dat"].dt.year()


def get_month_feature(df: pl.DataFrame) -> pl.Series:
    """
    Extract the month from the 't_dat' column.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pl.Series: A series containing the month extracted from 't_dat'.
    """
    return df["t_dat"].dt.month()


def get_day_feature(df: pl.DataFrame) -> pl.Series:
    """
    Extract the day from the 't_dat' column.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pl.Series: A series containing the day extracted from 't_dat'.
    """
    return df["t_dat"].dt.day()


def get_day_of_week_feature(df: pl.DataFrame) -> pl.Series:
    """
    Extract the day of the week from the 't_dat' column.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pl.Series: A series containing the day of the week extracted from 't_dat'.
    """
    return df["t_dat"].dt.weekday()


def calculate_month_sin_cos(month: pl.Series) -> pl.DataFrame:
    """
    Calculate sine and cosine values for the month to capture cyclical patterns.

    Parameters:
    - month (pl.Series): A series containing month values.

    Returns:
    - pl.DataFrame: A DataFrame with 'month_sin' and 'month_cos' columns.
    """
    C = 2 * np.pi / 12
    return pl.DataFrame(
        {
            "month_sin": month.apply(lambda x: np.sin(x * C)),
            "month_cos": month.apply(lambda x: np.cos(x * C)),
        }
    )


@udf(return_type = float, mode="pandas")
def month_sin(month :pd.Series):
    """
    On-demand transformation function that sine of month for cyclical feature encoding.

    Parameters:
    - month (pd.Series): A pandas series that contains the months

    Returns:
    - pd.Series: The sine of months
    """
    return np.sin(month * (2 * np.pi / 12))

@udf(return_type = float, mode="pandas")
def month_cos(month :pd.Series):
    """
    On-demand transformation function that sine of month for cyclical feature encoding.

    Parameters:
    - month (pd.Series): A pandas series that contains the months

    Returns:
    - pd.Series: The cosine of months
    """
    return np.cos(month * (2 * np.pi / 12))


def compute_features_transactions(df: pl.DataFrame) -> pl.DataFrame:
    """
    Prepare transaction data by performing several data transformations.

    Parameters:
    - df (pl.DataFrame): Input DataFrame containing transaction data.

    Returns:
    - pl.DataFrame: Processed DataFrame with transformed transaction data.
    """
    return (
        df.with_columns([
            pl.col("article_id").cast(pl.Utf8).alias("article_id"),
        ])
        .with_columns([
            pl.col("t_dat").dt.year().alias("year"),
            pl.col("t_dat").dt.month().alias("month"),
            pl.col("t_dat").dt.day().alias("day"),
            pl.col("t_dat").dt.weekday().alias("day_of_week"),
        ])
        .with_columns([
            # Convert datetime to epoch milliseconds
            (pl.col("t_dat").dt.timestamp() / 1_000).cast(pl.Int64).alias("t_dat")
        ])
    )
