import numpy as np
import pandas as pd


def haversine(long: int, lat: int, shift: int) -> float:
    """Compute Haversine distance between each consecutive coordinate in (long, lat).
    
    Args:
    - long: int ...
    - lat: int ...
    - shift: int ...
    Returns:
    - float: ...    
    """

    long_shifted = long.shift(shift)
    lat_shifted = lat.shift(shift)
    long_diff = long_shifted - long
    lat_diff = lat_shifted - lat

    a = np.sin(lat_diff / 2.0) ** 2
    b = np.cos(lat) * np.cos(lat_shifted) * np.sin(long_diff / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a + b))

    return c


def get_year_month(datetime_col: pd.Series) -> pd.Series:
    """Compute year and month string from datetime column.

    - datetime_col: pd.Series of datetime
    Returns:
    - pd.Series: year and month string
    """

    year_month = datetime_col.map(lambda x: str(x.year) + "-" + str(x.month))
    return year_month


def time_shift(datetime_col: pd.Series, shift: int) -> pd.Series:
    """Compute time difference between each consecutive transaction.

    Args:
    - datetime_col: pd.Series of datetime
    - shift: int value of time step
    Returns:
    - pd.Series:
    """
    time_shifted = datetime_col.shift(shift)
    return time_shifted


def loc_delta_t_minus_1(df: pd.DataFrame) -> pd.DataFrame:
    """Computes previous location of the transaction

    Args:
    - df: DataFrame that contains the transaction data
    Returns:
    - DataFrame: containing the new feature
     """
    df["loc_delta_t_minus_1"] = df.groupby("cc_num") \
        .apply(lambda x: haversine(x["longitude"], x["latitude"], -1)) \
        .reset_index(level=0, drop=True) \
        .fillna(0)
    df = df.drop_duplicates(subset=['cc_num', 'datetime']).reset_index(drop=True)
    return df


def time_delta_t_minus_1(df: pd.DataFrame) -> pd.DataFrame:
    """Computes time difference in days between current and previous transaction

    Args:
    - df: DataFrame that contains the transaction data
    Returns:
    - DataFrame: containing the new feature
     """
    df["time_delta_t_minus_1"] = df.groupby("cc_num") \
        .apply(lambda x: time_shift(x["datetime"], -1)) \
        .reset_index(level=0, drop=True)
    df["time_delta_t_minus_1"] = time_delta(df.time_delta_t_minus_1,  df.datetime, 'D')
    df["time_delta_t_minus_1"] = df.time_delta_t_minus_1.fillna(0)
    df["country"] = df["country"].fillna("US")
    df = df.drop_duplicates(subset=['cc_num', 'datetime']).reset_index(drop=True)
    return df


#
def card_owner_age(trans_df: pd.DataFrame, profiles_df: pd.DataFrame) -> pd.DataFrame:
    """Computes age of card owner at the time of transaction in years
    Args:
    - trans_df: pd.DataFrame
    - credit_cards_df: pd.DataFrame
    Returns:
    - pd.DataFrame:
    """
    age_df = trans_df.merge(profiles_df, on="cc_num", how="left")
    trans_df["age_at_transaction"] = time_delta(age_df["datetime"], age_df["birthdate"], 'Y')
    return trans_df


def expiry_days(trans_df: pd.DataFrame, profiles_df: pd.DataFrame) -> pd.DataFrame:
    """Computes days until card expires at the time of transaction
    Args:
    - trans_df: pd.DataFrame
    - credit_cards_df: pd.DataFrame
    Returns:
    - pd.DataFrame:
    """
    card_expiry_df = trans_df.merge(profiles_df, on="cc_num", how="left")
    trans_df["days_until_card_expires"] = \
        time_delta(card_expiry_df["cc_expiration_date"], card_expiry_df["datetime"], 'D')
    return trans_df


def is_merchant_abroad(trans_df: pd.DataFrame, profiles_df: pd.DataFrame) -> pd.DataFrame:
    """Computes if merchant location is abroad from card holders location
    Args:
    - trans_df: pd.DataFrame
    - credit_cards_df: pd.DataFrame
    Returns:
    - pd.DataFrame:
    """
    merged_df = trans_df.merge(profiles_df, on="cc_num", how="left")
    trans_df["is_merchant_abroad"] = merged_df["country"] == merged_df["country_of_residence"]
    return trans_df


def time_delta(date1: pd.Series, date2: pd.Series, unit: str) -> pd.Series:
    """Computes time difference in days between 2 pandas datetime series

    Args:
    - date1: pd.Series that contains datetime
    - date2: pd.Series that contains datetime
    - unit: time unit: 'D' or 'Y' days or years respectively
    Returns:
    - pd.Series: containing the time delta in units provided
     """
    return (date1 - date2) / np.timedelta64(1, unit)


def select_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Args:
    - df: DataFrame
    Returns:
    - DataFrame:
    """
    return df[
        ["tid", "datetime", "month", "cc_num", "amount", "country", "loc_delta_t_minus_1", "time_delta_t_minus_1",
         "days_until_card_expires", "age_at_transaction"]]