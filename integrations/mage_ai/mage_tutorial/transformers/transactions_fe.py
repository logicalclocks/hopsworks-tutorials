import numpy as np
import pandas as pd
from math import radians
from functions import haversine
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(trans_df, profiles_df, credit_cards_df, *args, **kwargs):
    """
    Feature Engineering for the transaction dataframe.

    Args:
        trans_df (pd.DataFrame): The DataFrame containing transaction data.
        profiles_df (pd.DataFrame): The DataFrame containing profiles data.
        credit_cards_df (pd.DataFrame): The DataFrame containing credit card data.
        *args: The output from any additional upstream blocks (if applicable).
        **kwargs: Additional keyword arguments.

    Returns:
        pd.DataFrame: The transformed DataFrame with additional columns.
    """
    # Merge the 'trans_df' DataFrame with the 'profiles_df' DataFrame based on the 'cc_num' column
    age_df = trans_df.merge(
        profiles_df, 
        on="cc_num",
         how="left",
         )

    # Compute the age at the time of each transaction and store it in the 'age_at_transaction' column
    trans_df["age_at_transaction"] = (
        age_df["datetime"] - age_df["birthdate"]
        ) / np.timedelta64(1, "Y")

    # Merge the 'trans_df' DataFrame with the 'credit_cards_df' DataFrame based on the 'cc_num' column
    card_expiry_df = trans_df.merge(
        credit_cards_df, 
        on="cc_num", 
        how="left",
        )

    # Convert the 'expires' column to datetime format
    card_expiry_df["expires"] = pd.to_datetime(
        card_expiry_df["expires"], 
        format="%m/%y",
        )

    # Compute the days until the card expires and store it in the 'days_until_card_expires' column
    trans_df["days_until_card_expires"] = (
        card_expiry_df["expires"] - card_expiry_df["datetime"]
        ) / np.timedelta64(1, "D")

    # Sort the 'trans_df' DataFrame based on the 'datetime' column in ascending order
    trans_df.sort_values("datetime", inplace=True)

    # Convert the 'longitude' and 'latitude' columns to radians
    trans_df[["longitude", "latitude"]] = trans_df[["longitude", "latitude"]].applymap(radians)

    # Apply the haversine function to compute the 'loc_delta' column
    trans_df["loc_delta"] = trans_df.groupby("cc_num")\
        .apply(lambda x : haversine(x["longitude"], x["latitude"]))\
        .reset_index(level=0, drop=True)\
        .fillna(0)

    return trans_df


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
