import pandas as pd
import numpy as np

def get_age_at_transaction(trans_df, profiles_df):
    """
    Calculate the age at transaction and add a new column 'age_at_transaction' to the DataFrame.

    Parameters:
    - trans_df (pd.DataFrame): DataFrame containing transaction data.
    - profiles_df (pd.DataFrame): DataFrame containing profiles data.

    Returns:
    - pd.DataFrame: Updated DataFrame with the 'age_at_transaction' column.
    """
    # Compute age at transaction.
    age_df = trans_df.merge(profiles_df, on="cc_num", how="left")
    trans_df["age_at_transaction"] = (age_df["datetime"] - age_df["birthdate"]) / np.timedelta64(1, "Y")
    return trans_df


def get_days_until_card_expires(trans_df, credit_cards_df):
    """
    Calculate the days until the card expires and add a new column 'days_until_card_expires' to the DataFrame.

    Parameters:
    - trans_df (pd.DataFrame): DataFrame containing transaction data.
    - credit_cards_df (pd.DataFrame): DataFrame containing credit cards data.

    Returns:
    - pd.DataFrame: Updated DataFrame with the 'days_until_card_expires' column.
    """
    # Compute days until card expires.
    card_expiry_df = trans_df.merge(credit_cards_df, on="cc_num", how="left")
    card_expiry_df["expires"] = pd.to_datetime(card_expiry_df["expires"], format="%m/%y")
    trans_df["days_until_card_expires"] = (card_expiry_df["expires"] - card_expiry_df["datetime"]) / np.timedelta64(1, "D")
    return trans_df


def haversine(long, lat):
    """
    Compute Haversine distance between each consecutive coordinate in (long, lat).

    Parameters:
    - long (pd.Series): Series containing longitude values.
    - lat (pd.Series): Series containing latitude values.

    Returns:
    - pd.Series: Haversine distances between consecutive coordinates.
    """
    long_shifted = long.shift()
    lat_shifted = lat.shift()
    long_diff = long_shifted - long
    lat_diff = lat_shifted - lat

    a = np.sin(lat_diff/2.0)**2
    b = np.cos(lat) * np.cos(lat_shifted) * np.sin(long_diff/2.0)**2
    c = 2*np.arcsin(np.sqrt(a + b))

    return c
