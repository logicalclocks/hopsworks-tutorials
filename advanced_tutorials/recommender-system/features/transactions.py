import pandas as pd
import numpy as np

def convert_article_id_to_str(df: pd.DataFrame) -> pd.Series:
    '''
    Converts the 'article_id' column to strings.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 'article_id' column.

    Returns:
    - pd.Series: Series containing the 'article_id' column as strings.
    '''
    return df["article_id"].astype(str)


def convert_t_dat_to_datetime(df: pd.DataFrame) -> pd.Series:
    '''
    Converts the 't_dat' column to datetime.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pd.Series: Series containing the 't_dat' column as datetime objects.
    '''
    return pd.to_datetime(df['t_dat'])


def get_year_feature(df: pd.DataFrame) -> pd.Series:
    '''
    Extracts and returns the 'year' feature from the 't_dat' column.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pd.Series: Series containing the 'year' feature.
    '''
    return df['t_dat'].dt.year


def get_month_feature(df: pd.DataFrame) -> pd.Series:
    '''
    Extracts and returns the 'month' feature from the 't_dat' column.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pd.Series: Series containing the 'month' feature.
    '''
    return df['t_dat'].dt.month


def get_day_feature(df: pd.DataFrame) -> pd.Series:
    '''
    Extracts and returns the 'day' feature from the 't_dat' column.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pd.Series: Series containing the 'day' feature.
    '''
    return df['t_dat'].dt.day


def get_day_of_week_feature(df: pd.DataFrame) -> pd.Series:
    '''
    Extracts and returns the 'day_of_week' feature from the 't_dat' column.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pd.Series: Series containing the 'day_of_week' feature.
    '''
    return df['t_dat'].dt.dayofweek


def calculate_month_sin_cos(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Calculates 'month_sin' and 'month_cos' columns based on the 'month' column.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 'month' column.

    Returns:
    - pd.DataFrame: DataFrame with new 'month_sin' and 'month_cos' columns.
    '''
    C = 2 * np.pi / 12
    df['month_sin'] = np.sin(df['month'] * C)
    df['month_cos'] = np.cos(df['month'] * C)
    return df


def convert_t_dat_to_epoch_milliseconds(df: pd.DataFrame) -> pd.Series:
    '''
    Converts 't_dat' column values to Unix epoch milliseconds.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 't_dat' column.

    Returns:
    - pd.Series: Series containing 't_dat' values converted to Unix epoch milliseconds.
    '''
    return df.t_dat.values.astype(np.int64) // 10 ** 6


def prepare_transactions(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Prepares the input DataFrame by applying various transformations on each column.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: Processed DataFrame with new features.
    '''
    # Convert 'article_id' to strings
    df["article_id"] = convert_article_id_to_str(df)

    # Convert 't_dat' to datetime
    df['t_dat'] = convert_t_dat_to_datetime(df)

    # Add individual date features to the original DataFrame
    df['year'] = get_year_feature(df)
    df['month'] = get_month_feature(df)
    df['day'] = get_day_feature(df)
    df['day_of_week'] = get_day_of_week_feature(df)

    # Calculate 'month_sin' and 'month_cos'
    df = calculate_month_sin_cos(df)

    # Convert 't_dat' to epoch milliseconds
    df['t_dat'] = convert_t_dat_to_epoch_milliseconds(df)

    return df
