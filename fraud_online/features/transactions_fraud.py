from math import radians
import numpy as np


def haversine(long, lat, shift):
    """Compute Haversine distance between each consecutive coordinate in (long, lat)."""

    long_shifted = long.shift(shift)
    lat_shifted = lat.shift(shift)
    long_diff = long_shifted - long
    lat_diff = lat_shifted - lat

    a = np.sin(lat_diff/2.0)**2
    b = np.cos(lat) * np.cos(lat_shifted) * np.sin(long_diff/2.0)**2
    c = 2*np.arcsin(np.sqrt(a + b))

    return c


def time_delta(datetime_value, shift):
    """Compute time difference between each consecutive transaction."""

    time_shifted = datetime_value.shift(shift)
    return time_shifted


def prepare_transactions_fraud(trans_df):
    trans_df.sort_values("datetime", inplace=True)
    trans_df[["longitude", "latitude"]] = trans_df[["longitude", "latitude"]].applymap(radians)

    trans_df["loc_delta_t_plus_1"] = trans_df.groupby("cc_num")\
        .apply(lambda x : haversine(x["longitude"], x["latitude"], 1))\
        .reset_index(level=0, drop=True)\
        .fillna(0)

    trans_df["loc_delta_t_minus_1"] = trans_df.groupby("cc_num")\
        .apply(lambda x : haversine(x["longitude"], x["latitude"], -1))\
        .reset_index(level=0, drop=True)\
        .fillna(0)

    trans_df["time_delta_t_minus_1"] = trans_df.groupby("cc_num")\
        .apply(lambda x : time_delta(x["datetime"],  -1))\
        .reset_index(level=0, drop=True)

    trans_df["time_delta_t_minus_1"] = (trans_df.time_delta_t_minus_1 - trans_df.datetime )/ np.timedelta64(1, 'D')
    trans_df["time_delta_t_minus_1"] = trans_df.time_delta_t_minus_1.fillna(0)  

    trans_df = trans_df[["tid", "datetime", "cc_num", "amount", "country", "fraud_label",
                     "loc_delta_t_plus_1", "loc_delta_t_minus_1", "time_delta_t_minus_1"]]
    
    trans_df = trans_df.drop_duplicates(subset=['cc_num', 'datetime']) \
               .reset_index(drop=True)
    
    return trans_df

