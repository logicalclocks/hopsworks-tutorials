import pandas as pd

def get_window_aggs_df(window_len: int, trans_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various window aggregates based on transaction data.

    Parameters:
    - window_len (int): Window length for rolling calculations.
    - trans_df (pd.DataFrame): DataFrame containing transaction data.

    Returns:
    - pd.DataFrame: DataFrame with calculated window aggregates.
    """
    # Group by credit card number and apply rolling window calculations
    cc_group = trans_df[["cc_num", "amount", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime")

    # Moving average of transaction volume.
    df_mavg = pd.DataFrame(cc_group.mean())
    df_mavg.columns = ["trans_volume_mavg", "datetime"]
    df_mavg = df_mavg.reset_index(level=["cc_num"])
    df_mavg = df_mavg.drop(columns=["cc_num", "datetime"])
    df_mavg = df_mavg.sort_index()

    # Moving standard deviation of transaction volume.
    df_std = pd.DataFrame(cc_group.std())
    df_std.columns = ["trans_volume_mstd", "datetime"]
    df_std = df_std.reset_index(level=["cc_num"])
    df_std = df_std.drop(columns=["cc_num", "datetime"])
    df_std = df_std.fillna(0)
    df_std = df_std.sort_index()
    window_aggs_df = df_std.merge(
        df_mavg,
        left_index=True, 
        right_index=True,
    )

    # Moving average of transaction frequency.
    df_count = pd.DataFrame(cc_group.count())
    df_count.columns = ["trans_freq", "datetime"]
    df_count = df_count.reset_index(level=["cc_num"])
    df_count = df_count.drop(columns=["cc_num", "datetime"])
    df_count = df_count.sort_index()
    window_aggs_df = window_aggs_df.merge(
        df_count,
        left_index=True, 
        right_index=True,
    )

    # Moving average of location difference between consecutive transactions.
    cc_group = trans_df[["cc_num", "loc_delta", "datetime"]].groupby("cc_num").rolling(
        window_len, 
        on="datetime"
    ).mean()
    df_loc_delta_mavg = pd.DataFrame(cc_group)
    df_loc_delta_mavg.columns = ["loc_delta_mavg", "datetime"]
    df_loc_delta_mavg = df_loc_delta_mavg.reset_index(level=["cc_num"])
    df_loc_delta_mavg = df_loc_delta_mavg.drop(columns=["cc_num", "datetime"])
    df_loc_delta_mavg = df_loc_delta_mavg.sort_index()
    window_aggs_df = window_aggs_df.merge(
        df_loc_delta_mavg,
        left_index=True, 
        right_index=True,
    )

    window_aggs_df = window_aggs_df.merge(
        trans_df[["cc_num", "datetime"]].sort_index(),
        left_index=True, 
        right_index=True,
    )

    return window_aggs_df