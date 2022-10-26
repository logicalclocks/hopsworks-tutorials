import math
import requests
import zipfile
import enlighten
from io import BytesIO
import os
import json

import pandas as pd
from tqdm import tqdm

import warnings

# Mute warnings
warnings.filterwarnings("ignore")

def process_df(original_df):
    res = original_df[["started_at", "start_station_id"]]
    res.started_at = pd.to_datetime(res.started_at)
    res.started_at = res.started_at.dt.floor('d')
    res = res.groupby(["started_at",
                       "start_station_id"]).value_counts().reset_index()
    res = res.rename(columns={"started_at": "date",
                              "start_station_id": "station_id",
                              0: "users_count"})
    return res


def update_month_data(main_df, month, year):
    if month < 10:
        month = f"0{month}"
    print(f"_____ Processing {month}/{year}... _____")

    url = f'https://s3.amazonaws.com/tripdata/{year}{month}-citibike-tripdata.csv.zip'
    filename = "data/" + url.split('/')[-1].split(".")[0] + ".csv"
    fn_list = filename.split(".")
    processed_filename = fn_list[-2] + "_processed." + fn_list[-1]

    if os.path.isfile(processed_filename):
        print("Retrieving DataFrame from the existing csv file...💿")
        return pd.concat([pd.read_csv(processed_filename, index_col=0), main_df])

    print('Downloading Started...⏳')

    req = requests.get(url)

    print('Downloading Completed!👌')

    file= zipfile.ZipFile(BytesIO(req.content))

    file.extractall("data/")

    print("Retrieving DataFrame from the csv file...💿")
    print("-" * 32)

    original_df = pd.read_csv(filename)

    # check if there is a file with station ids, names, coords mapping
    if not os.path.isfile("data/stations_info.json"):
        clipped_df = original_df[["start_station_id", "start_station_name",
                                  "start_lat", "start_lng"]].drop_duplicates()
        stations_info_dict = {
            row[0]: {
                "station_name": row[1],
                "coords": row[2:]
                } for row in clipped_df.itertuples(index=False)}

        with open('data/stations_info.json', 'w') as fp:
            json.dump(stations_info_dict, fp)

    processed_df = process_df(original_df)

    # delete original big unprocessed file
    os.remove(filename)

    # save processed file in csv
    processed_df.to_csv(processed_filename, index=False)

    return pd.concat([processed_df, main_df])



def get_citibike_data(start_date="04/2021", end_date="10/2022") -> pd.DataFrame:

    start_month, start_year = start_date.split("/")[0], start_date.split("/")[1]
    end_month, end_year = end_date.split("/")[0], end_date.split("/")[1]

    res = pd.DataFrame(columns=["date", "station_id", "users_count"])

    if start_year == end_year:
        for month in range(int(start_month), int(end_month) + 1):
            res =  update_month_data(res, month, start_year)

    else:
        for month in range(int(start_month), 13):
            res =  update_month_data(res, month, start_year)
        for month in range(1, int(end_month) + 1):
            res =  update_month_data(res, month, end_year)

    return res.reset_index(drop=True)


################################################################################
# Data preprocessing

def moving_average(df, window=7):
    df[f'mean_{window}_days'] = df["users_count"].rolling(window=window).mean()
    return df


def moving_std(df, window):
    df[f'std_{window}_days'] = df["users_count"].rolling(window=window).std()
    return df


def exponential_moving_average(df, window):
    df[f'exp_mean_{window}_days'] = df["users_count"].ewm(span=window).mean()
    return df


def exponential_moving_std(df, window):
    df[f'exp_std_{window}_days'] = df["users_count"].ewm(span=window).std()
    return df


def rate_of_change(df, window):
    M = df["users_count"].diff(window - 1)
    N = df["users_count"].shift(window - 1)
    df[f'rate_of_change_{window}_days'] = (M / N) * 100
    return df


def engineer_citibike_features(df):
    res = df.copy()
    res = moving_average(res, 7).dropna()
    res = moving_average(res, 14).dropna()
    res = moving_average(res, 56).dropna()


    for i in [7, 14, 56]:
        for func in [moving_std, exponential_moving_average,
                     exponential_moving_std, rate_of_change
                     ]:
            res = func(res, i).dropna()
    return res.reset_index(drop=True)
