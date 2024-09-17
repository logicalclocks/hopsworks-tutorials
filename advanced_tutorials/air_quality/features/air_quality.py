from typing import Union
import pandas as pd
import numpy as np

###########################################################################################
# Part 1: Air Quality Features

def shift_pm_2_5(df: pd.DataFrame, days: int = 5) -> pd.DataFrame:
    """
    Shift the 'pm2_5' values in the DataFrame by a specified number of days for each city.

    Parameters:
    - df (pd.DataFrame): DataFrame containing air quality data.
    - days (int): Number of days to shift the 'pm2_5' values. Default is 5.

    Returns:
    - pd.DataFrame: DataFrame with additional columns for shifted 'pm2_5' values.
    """
    for shift_value in range(1, days + 1):
        df[f'pm_2_5_previous_{shift_value}_day'] = df.groupby('city_name')['pm2_5'].shift(shift_value)
    return df


def moving_average(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """
    Calculate the moving average of 'pm2_5' values for each city over a specified window.

    Parameters:
    - df (pd.DataFrame): DataFrame containing air quality data.
    - window (int): Size of the moving average window. Default is 7.

    Returns:
    - pd.DataFrame: DataFrame with an additional column for the moving average.
    """
    df[f'mean_{window}_days'] = df.groupby('city_name')['pm2_5'] \
                                    .rolling(window=window).mean().reset_index(0, drop=True).shift(1)
    return df


def moving_std(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculate the moving standard deviation of 'pm2_5' values for each city over a specified window.

    Parameters:
    - df (pd.DataFrame): DataFrame containing air quality data.
    - window (int): Size of the moving standard deviation window.

    Returns:
    - pd.DataFrame: DataFrame with an additional column for the moving standard deviation.
    """
    df[f'std_{window}_days'] = df.groupby('city_name')['pm2_5'] \
                                    .rolling(window=window).std().reset_index(0, drop=True).shift(1)
    return df


def exponential_moving_average(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculate the exponential moving average of 'pm2_5' values for each city over a specified window.

    Parameters:
    - df (pd.DataFrame): DataFrame containing air quality data.
    - window (int): Span of the exponential moving average window.

    Returns:
    - pd.DataFrame: DataFrame with an additional column for the exponential moving average.
    """
    df[f'exp_mean_{window}_days'] = df.groupby('city_name')['pm2_5'].ewm(span=window) \
                                        .mean().reset_index(0, drop=True).shift(1)
    return df


def exponential_moving_std(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculate the exponential moving standard deviation of 'pm2_5' values for each city over a specified window.

    Parameters:
    - df (pd.DataFrame): DataFrame containing air quality data.
    - window (int): Span of the exponential moving standard deviation window.

    Returns:
    - pd.DataFrame: DataFrame with an additional column for the exponential moving standard deviation.
    """
    df[f'exp_std_{window}_days'] = df.groupby('city_name')['pm2_5'].ewm(span=window) \
                                        .std().reset_index(0, drop=True).shift(1)
    return df

###########################################################################################
# Part 2: Date and Time Features

def year(date_column: pd.Series) -> pd.Series:
    """
    Extracts the year from the 'date' column and returns it as a new feature.

    Parameters:
    - date_column (pd.Series): Series containing date values.

    Returns:
    - pd.Series: Series with the 'year' feature.
    """
    return date_column.dt.year.astype(int)


def day_of_month(date_column: pd.Series) -> pd.Series:
    """
    Extracts the day of the month from the 'date' column and returns it as a new feature.

    Parameters:
    - date_column (pd.Series): Series containing date values.

    Returns:
    - pd.Series: Series with the 'day_of_month' feature.
    """
    return date_column.dt.day.astype(int)


def month(date_column: pd.Series) -> pd.Series:
    """
    Extracts the month from the 'date' column and returns it as a new feature.

    Parameters:
    - date_column (pd.Series): Series containing date values.

    Returns:
    - pd.Series: Series with the 'month' feature.
    """
    return date_column.dt.month.astype(int)


def day_of_week(date_column: pd.Series) -> pd.Series:
    """
    Extracts the day of the week from the 'date' column and returns it as a new feature.

    Parameters:
    - date_column (pd.Series): Series containing date values.

    Returns:
    - pd.Series: Series with the 'day_of_week' feature.
    """
    return date_column.dt.dayofweek.astype(int)


def is_weekend(day_of_week_col: pd.Series) -> pd.Series:
    """
    Adds a binary feature indicating whether the day is a weekend (1) or not (0).

    Parameters:
    - day_of_week_col (pd.Series): Series containing day of the week values.

    Returns:
    - pd.Series: Series with the 'is_weekend' feature.
    """
    return np.where(day_of_week_col.isin([5, 6]), 1, 0)


def sin_day_of_year(date_column: pd.Series) -> pd.Series:
    """
    Calculates the sine of the day of the year and returns it as a new feature.

    Parameters:
    - date_column (pd.Series): Series containing date values.

    Returns:
    - pd.Series: Series with the 'sin_day_of_year' feature.
    """
    day_of_year = date_column.dt.dayofyear
    return np.sin(2 * np.pi * day_of_year / 365)


def cos_day_of_year(date_column: pd.Series) -> pd.Series:
    """
    Calculates the cosine of the day of the year and returns it as a new feature.

    Parameters:
    - date_column (pd.Series): Series containing date values.

    Returns:
    - pd.Series: Series with the 'cos_day_of_year' feature.
    """
    day_of_year = date_column.dt.dayofyear
    return np.cos(2 * np.pi * day_of_year / 365)


def sin_day_of_week(day_of_week_col: pd.Series) -> pd.Series:
    """
    Calculates the sine of the day of the week and returns it as a new feature.

    Parameters:
    - day_of_week_col (pd.Series): Series containing day of the week values.

    Returns:
    - pd.Series: Series with the 'sin_day_of_week' feature.
    """
    return np.sin(2 * np.pi * day_of_week_col / 7)


def cos_day_of_week(day_of_week_col: pd.Series) -> pd.Series:
    """
    Calculates the cosine of the day of the week and returns it as a new feature.

    Parameters:
    - day_of_week_col (pd.Series): Series containing day of the week values.

    Returns:
    - pd.Series: Series with the 'cos_day_of_week' feature.
    """
    return np.cos(2 * np.pi * day_of_week_col / 7)


def feature_engineer_aq(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs multiple feature engineering tasks on the input DataFrame related to air quality.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing 'date', 'city_name', and 'pm2_5' columns.

    Returns:
    - pd.DataFrame: DataFrame with additional engineered features.
    """
    df_res = df.copy()

    df_res = shift_pm_2_5(df_res, days=7) 
    df_res = moving_average(df_res, 7)
    df_res = moving_average(df_res, 14)
    df_res = moving_average(df_res, 28)

    for i in [7, 14, 28]:
        for func in [moving_std, exponential_moving_average, exponential_moving_std]:
            df_res = func(df_res, i)
    
    
    df_res = df_res.sort_values(by=["date", "pm2_5"])
    df_res = df_res.reset_index(drop=True)

    df_res['year'] = year(df_res['date'])
    df_res['day_of_month'] = day_of_month(df_res['date'])
    df_res['month'] = month(df_res['date'])
    df_res['day_of_week'] = day_of_week(df_res['date'])
    df_res['is_weekend'] = is_weekend(df_res['day_of_week'])
    df_res['sin_day_of_year'] = sin_day_of_year(df_res['date'])
    df_res['cos_day_of_year'] = cos_day_of_year(df_res['date'])
    df_res['sin_day_of_week'] = sin_day_of_week(df_res['day_of_week'])
    df_res['cos_day_of_week'] = cos_day_of_week(df_res['day_of_week'])

    return df_res
