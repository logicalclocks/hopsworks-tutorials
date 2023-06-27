import pandas as pd


def get_window_aggs_df(window_len, trans_df):
    cc_group = trans_df[["cc_num", "amount", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime")

    # Moving average of transaction volume.
    df_4h_mavg = pd.DataFrame(cc_group.mean())
    df_4h_mavg.columns = ["trans_volume_mavg", "datetime"]
    df_4h_mavg = df_4h_mavg.reset_index(level=["cc_num"])
    df_4h_mavg = df_4h_mavg.drop(columns=["cc_num", "datetime"])
    df_4h_mavg = df_4h_mavg.sort_index()

    # Moving standard deviation of transaction volume.
    df_4h_std = pd.DataFrame(cc_group.std())
    df_4h_std.columns = ["trans_volume_mstd", "datetime"]
    df_4h_std = df_4h_std.reset_index(level=["cc_num"])
    df_4h_std = df_4h_std.drop(columns=["cc_num", "datetime"])
    df_4h_std = df_4h_std.fillna(0)
    df_4h_std = df_4h_std.sort_index()
    window_aggs_df = df_4h_std.merge(df_4h_mavg,left_index=True, right_index=True)

    # Moving average of transaction frequency.
    df_4h_count = pd.DataFrame(cc_group.count())
    df_4h_count.columns = ["trans_freq", "datetime"]
    df_4h_count = df_4h_count.reset_index(level=["cc_num"])
    df_4h_count = df_4h_count.drop(columns=["cc_num", "datetime"])
    df_4h_count = df_4h_count.sort_index()
    window_aggs_df = window_aggs_df.merge(df_4h_count,left_index=True, right_index=True)

    # Moving average of location difference between consecutive transactions.
    cc_group = trans_df[["cc_num", "loc_delta", "datetime"]].groupby("cc_num").rolling(window_len, on="datetime").mean()
    df_4h_loc_delta_mavg = pd.DataFrame(cc_group)
    df_4h_loc_delta_mavg.columns = ["loc_delta_mavg", "datetime"]
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.reset_index(level=["cc_num"])
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.drop(columns=["cc_num", "datetime"])
    df_4h_loc_delta_mavg = df_4h_loc_delta_mavg.sort_index()
    window_aggs_df = window_aggs_df.merge(df_4h_loc_delta_mavg,left_index=True, right_index=True)

    window_aggs_df = window_aggs_df.merge(trans_df[["cc_num", "datetime"]].sort_index(),left_index=True, right_index=True)

    return window_aggs_df