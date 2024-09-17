import pandas as pd
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(trans_df, *args, **kwargs):
    """
    Compute the dataframe with window aggregations.

    Args:
        trans_df (pd.DataFrame): The DataFrame containing transaction data.
        *args: The output from any additional upstream blocks (if applicable).
        **kwargs: Additional keyword arguments.

    Returns:
        pd.DataFrame: The transformed DataFrame with aggregated window features.
    """
    # Specify the window length as "4h"
    window_len = "4h"   

    # Define a rolling window groupby on 'cc_num' with a specified window length on the 'datetime' column
    cc_group = trans_df[["cc_num", "amount", "datetime"]].groupby("cc_num").rolling(
        window_len, 
        on="datetime",
    )

    # Moving average of transaction volume.
    df_4h_mavg = pd.DataFrame(cc_group.mean())
    df_4h_mavg.columns = ["trans_volume_mavg", "datetime"]
    df_4h_mavg = df_4h_mavg.reset_index(level=["cc_num"])
    df_4h_mavg = df_4h_mavg.drop(columns=["cc_num", "datetime"])
    df_4h_mavg = df_4h_mavg.sort_index()

    # Moving standard deviation of transaction volume.
    df_4h_std = pd.DataFrame(cc_group.mean())
    df_4h_std.columns = ["trans_volume_mstd", "datetime"]
    df_4h_std = df_4h_std.reset_index(level=["cc_num"])
    df_4h_std = df_4h_std.drop(columns=["cc_num", "datetime"])
    df_4h_std = df_4h_std.fillna(0)
    df_4h_std = df_4h_std.sort_index()
    window_aggs_df = df_4h_std.merge(df_4h_mavg, left_index=True, right_index=True)

    # Moving average of transaction frequency.
    df_4h_count = pd.DataFrame(cc_group.mean())
    df_4h_count.columns = ["trans_freq", "datetime"]
    df_4h_count = df_4h_count.reset_index(level=["cc_num"])
    df_4h_count = df_4h_count.drop(columns=["cc_num", "datetime"])
    df_4h_count = df_4h_count.sort_index()
    window_aggs_df = window_aggs_df.merge(df_4h_count, left_index=True, right_index=True)

    # Moving average of location difference between consecutive transactions.
    cc_group_loc_delta = trans_df[["cc_num", "loc_delta", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime").mean()
    df_4h_loc_delta_mavg = pd.DataFrame(cc_group_loc_delta)
    df_4h_loc_delta_mavg.columns = ["loc_delta_mavg", "datetime"]
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.reset_index(level=["cc_num"])
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.drop(columns=["cc_num", "datetime"])
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.sort_index()
    window_aggs_df = window_aggs_df.merge(df_4h_loc_delta_mavg, left_index=True, right_index=True)

    # Merge 'trans_df' with selected columns for the final result
    window_aggs_df = window_aggs_df.merge(
        trans_df[["cc_num", "datetime"]].sort_index(), 
        left_index=True, 
        right_index=True,
    )

    return window_aggs_df


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
