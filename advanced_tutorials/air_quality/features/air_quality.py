from typing import Union
import pandas as pd
import numpy as np

###########################################################################################
# Part 1: Air Quality Features

def shift_pm_2_5(df: pd.DataFrame, days: int = 5) -> pd.Series:
    """
    Shifts the 'pm2_5' values in the DataFrame for a specified number of days.

    Args:
        df (pd.DataFrame): Input DataFrame containing 'date', 'city_name', and 'pm2_5' columns.
        days (int): Number of days to shift the 'pm2_5' values.

    Returns:
        pd.Series: Series with shifted 'pm2_5' values.
    """
    # Convert 'pm2_5' column to numeric to handle potential non-numeric values
    df['pm2_5'] = pd.to_numeric(df['pm2_5'], errors='coerce')

    # Group by 'city_name' and transform to shift 'pm2_5' values within each group
    shifted_series = df.groupby('city_name')['pm2_5'].transform(lambda x: x.shift(days))

    return shifted_series


def moving_average(df: pd.DataFrame, window: int = 7) -> pd.Series:
    """
    Calculates the moving average of 'pm2_5' values in the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame containing 'date', 'city_name', and 'pm2_5' columns.
        window (int): Size of the moving average window.

    Returns:
        pd.Series: Series with the moving average of 'pm2_5' values.
    """
    return df.groupby('city_name')['pm2_5'].rolling(window=window).mean().reset_index(0, drop=True).shift(1)


def moving_std(df: pd.DataFrame, window: int) -> pd.Series:
    """
    Calculates the moving standard deviation of 'pm2_5' values in the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame containing 'date', 'city_name', and 'pm2_5' columns.
        window (int): Size of the moving standard deviation window.

    Returns:
        pd.Series: Series with the moving standard deviation of 'pm2_5' values.
    """
    return df.groupby('city_name')['pm2_5'].rolling(window=window).std().reset_index(0, drop=True).shift(1)


def exponential_moving_average(df: pd.DataFrame, window: int) -> pd.Series:
    """
    Calculates the exponential moving average of 'pm2_5' values in the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame containing 'date', 'city_name', and 'pm2_5' columns.
        window (int): Span of the exponential moving average.

    Returns:
        pd.Series: Series with the exponential moving average of 'pm2_5' values.
    """
    return df.groupby('city_name')['pm2_5'].ewm(span=window).mean().reset_index(0, drop=True).shift(1)


def exponential_moving_std(df: pd.DataFrame, window: int) -> pd.Series:
    """
    Calculates the exponential moving standard deviation of 'pm2_5' values in the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame containing 'date', 'city_name', and 'pm2_5' columns.
        window (int): Span of the exponential moving standard deviation.

    Returns:
        pd.Series: Series with the exponential moving standard deviation of 'pm2_5' values.
    """
    return df.groupby('city_name')['pm2_5'].ewm(span=window).std().reset_index(0, drop=True).shift(1)

###########################################################################################
# Part 2: Date and Time Features

def year(df: pd.DataFrame) -> pd.Series:
    """
    Extracts the year from the 'date' column and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'date' column.

    Returns:
        pd.Series: Series with the 'year' feature.
    """
    return df['date'].dt.year.astype(int)


def day_of_month(df: pd.DataFrame) -> pd.Series:
    """
    Extracts the day of the month from the 'date' column and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'date' column.

    Returns:
        pd.Series: Series with the 'day_of_month' feature.
    """
    return df['date'].dt.day.astype(int)


def month(df: pd.DataFrame) -> pd.Series:
    """
    Extracts the month from the 'date' column and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'date' column.

    Returns:
        pd.Series: Series with the 'month' feature.
    """
    return df['date'].dt.month.astype(int)


def day_of_week(df: pd.DataFrame) -> pd.Series:
    """
    Extracts the day of the week from the 'date' column and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'date' column.

    Returns:
        pd.Series: Series with the 'day_of_week' feature.
    """
    return df['date'].dt.dayofweek.astype(int)


def is_weekend(df: pd.DataFrame) -> pd.Series:
    """
    Adds a binary feature indicating whether the day is a weekend (1) or not (0).

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'day_of_week' column.

    Returns:
        pd.Series: Series with the 'is_weekend' feature.
    """
    return np.where(df['day_of_week'].isin([5, 6]), 1, 0)


def sin_day_of_year(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the sine of the day of the year and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'date' column.

    Returns:
        pd.Series: Series with the 'sin_day_of_year' feature.
    """
    day_of_year = df['date'].dt.dayofyear
    return np.sin(2 * np.pi * day_of_year / 365)


def cos_day_of_year(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the cosine of the day of the year and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'date' column.

    Returns:
        pd.Series: Series with the 'cos_day_of_year' feature.
    """
    day_of_year = df['date'].dt.dayofyear
    return np.cos(2 * np.pi * day_of_year / 365)


def sin_day_of_week(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the sine of the day of the week and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'day_of_week' column.

    Returns:
        pd.Series: Series with the 'sin_day_of_week' feature.
    """
    return np.sin(2 * np.pi * df['day_of_week'] / 7)


def cos_day_of_week(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the cosine of the day of the week and returns it as a new feature.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'day_of_week' column.

    Returns:
        pd.Series: Series with the 'cos_day_of_week' feature.
    """
    return np.cos(2 * np.pi * df['day_of_week'] / 7)


def feature_engineer_aq(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs multiple feature engineering tasks on the input DataFrame related to air quality.

    Args:
        df (pd.DataFrame): Input DataFrame containing 'date', 'city_name', and 'pm2_5' columns.

    Returns:
        pd.DataFrame: DataFrame with additional engineered features.
    """
    df_res = df.copy()

    df_res['pm_2_5_shifted'] = shift_pm_2_5(df_res, days=7)
    df_res['mean_7_days'] = moving_average(df_res, window=7)
    df_res['mean_14_days'] = moving_average(df_res, window=14)
    df_res['mean_28_days'] = moving_average(df_res, window=28)

    for i in [7, 14, 28]:
        df_res[f'std_{i}_days'] = moving_std(df_res, window=i)
        df_res[f'exp_mean_{i}_days'] = exponential_moving_average(df_res, window=i)
        df_res[f'exp_std_{i}_days'] = exponential_moving_std(df_res, window=i)

    df_res = df_res.sort_values(by=["date", "pm2_5"]).dropna()
    df_res = df_res.reset_index(drop=True)

    df_res['year'] = year(df_res)
    df_res['day_of_month'] = day_of_month(df_res)
    df_res['month'] = month(df_res)
    df_res['day_of_week'] = day_of_week(df_res)
    df_res['is_weekend'] = is_weekend(df_res)
    df_res['sin_day_of_year'] = sin_day_of_year(df_res)
    df_res['cos_day_of_year'] = cos_day_of_year(df_res)
    df_res['sin_day_of_week'] = sin_day_of_week(df_res)
    df_res['cos_day_of_week'] = cos_day_of_week(df_res)

    return df_res