import math
import requests
import joblib
from datetime import datetime
import zipfile
from io import BytesIO
import os
import json

import pandas as pd

# Mute warnings
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()


def select_stations_info(df):
    df_res = df[["start_station_id", "start_station_name",
                 "start_lat", "start_lng"]].rename(
                                                  columns={
                                                  "start_station_id": "station_id",
                                                  "start_station_name": "station_name",
                                                  "start_lat": "lat",
                                                  "start_lng": "long"}
                                                  )
    df_res = df_res.drop_duplicates()
    return df_res


def process_df(original_df):
    df_res = original_df[["started_at", "start_station_id"]]
    df_res.started_at = pd.to_datetime(df_res.started_at)
    df_res.started_at = df_res.started_at.dt.floor('d')
    df_res = df_res.groupby(["started_at",
                             "start_station_id"]).value_counts().reset_index()
    df_res = df_res.rename(columns={"started_at": "date",
                                    "start_station_id": "station_id",
                                    0: "users_count"})
    return df_res


def update_month_data(main_df, month, year):
    if month < 10:
        month = f"0{month}"
    print(f"_____ Processing {month}/{year}... _____")

    if f"{year}{month}" in ["202206", "202207"]:
        citibike = "citbike"
    else:
        citibike = "citibike"
    url = f'https://s3.amazonaws.com/tripdata/{year}{month}-{citibike}-tripdata.csv.zip'
    print(url)
    filename = "data/" + url.split('/')[-1].split(".")[0] + ".csv"
    fn_list = filename.split(".")
    processed_filename = fn_list[-2] + "_processed." + fn_list[-1]

    if os.path.isfile(processed_filename):
        print("Retrieving DataFrame from the existing csv file...💿")
        return pd.concat([pd.read_csv(processed_filename), main_df])

    print('Downloading Started...⏳')

    req = requests.get(url)

    print('Downloading Completed!👌')

    file= zipfile.ZipFile(BytesIO(req.content))

    file.extractall("data/")

    print("Retrieving DataFrame from the csv file...💿")
    print("-" * 32)

    original_df = pd.read_csv(filename)

    if not os.path.isfile("data/stations_info.csv"):
        stations_info_df = select_stations_info(original_df)
        stations_info_df.to_csv("data/stations_info.csv", index=False)

    processed_df = process_df(original_df)

    # delete original big unprocessed file
    os.remove(filename)

    # save processed file in csv
    processed_df.to_csv(processed_filename, index=False)

    return pd.concat([processed_df, main_df])


def get_citibike_data(start_date="04/2021", end_date="10/2022") -> pd.DataFrame:

    start_month, start_year = start_date.split("/")[0], start_date.split("/")[1]
    end_month, end_year = end_date.split("/")[0], end_date.split("/")[1]

    df_res = pd.DataFrame(columns=["date", "station_id", "users_count"])

    if start_year == end_year:
        for month in range(int(start_month), int(end_month) + 1):
            df_res =  update_month_data(df_res, month, start_year)

    else:
        for month in range(int(start_month), 13):
            df_res =  update_month_data(df_res, month, start_year)
        for month in range(1, int(end_month) + 1):
            df_res =  update_month_data(df_res, month, end_year)

    df_res["users_count"] = df_res["users_count"].astype(int)

    print("\n✅ Done ✅")

    return df_res.reset_index(drop=True)


################################################################################
# Data engineering

def convert_date_to_unix(x):
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


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
    df[f'rate_of_change_{window}_days'] = df[f'rate_of_change_{window}_days'].astype(float)
    return df


def engineer_citibike_features(df):
    df_res = df.copy()
    df_res['users_count_next_day'] = df_res.groupby('station_id')['users_count'].shift(-1)
    df_res = moving_average(df_res, 7).dropna()
    df_res = moving_average(df_res, 14).dropna()
    df_res = moving_average(df_res, 56).dropna()


    for i in [7, 14, 56]:
        for func in [moving_std, exponential_moving_average,
                     exponential_moving_std, rate_of_change
                     ]:
            df_res = func(df_res, i).dropna()
    df_res = df_res.reset_index(drop=True)
    return df_res


###############################################################################
# Weather parsing

def parse_weather_data(city, start_date, end_date, API_KEY):
    # yyyy-MM-DD data format
    formatted_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{start_date}/{end_date}?unitGroup=metric&include=days&key={API_KEY}&contentType=csv"
    return pd.read_csv(formatted_url)


def get_weather_data(city, start_date, end_date):
    API_KEY = os.getenv("VISUALCROSSING_API_KEY")
    # API_KEY = ""

    df_res = parse_weather_data(city, start_date, end_date, API_KEY)
    # drop redundant columns
    df_res = df_res.drop(columns=["name", "icon", "stations", "description",
                                  "sunrise", "sunset", "preciptype",
                                  "severerisk", "conditions"])

    df_res = df_res.rename(columns={"datetime": "date"})

    return df_res


###############################################################################
# Streamlit
def decode_features(df, feature_view):
    """Decodes features in the input DataFrame using corresponding Hopsworks Feature Store transformation functions"""
    df_res = df.copy()

    import inspect

    print(feature_view)
    td_transformation_functions = feature_view._batch_scoring_server._transformation_functions

    res = {}
    for feature_name in td_transformation_functions:
        if feature_name in df_res.columns:
            td_transformation_function = td_transformation_functions[feature_name]
            sig, foobar_locals = inspect.signature(td_transformation_function.transformation_fn), locals()
            param_dict = dict([(param.name, param.default) for param in sig.parameters.values() if param.default != inspect._empty])
            if td_transformation_function.name == "min_max_scaler":
                df_res[feature_name] = df_res[feature_name].map(
                    lambda x: x * (param_dict["max_value"] - param_dict["min_value"]) + param_dict["min_value"])

            elif td_transformation_function.name == "standard_scaler":
                df_res[feature_name] = df_res[feature_name].map(
                    lambda x: x * param_dict['std_dev'] + param_dict["mean"])
            elif td_transformation_function.name == "label_encoder":
                dictionary = param_dict['value_to_index']
                dictionary_ = {v: k for k, v in dictionary.items()}
                df_res[feature_name] = df_res[feature_name].map(
                    lambda x: dictionary_[x])
    return df_res


def get_model():
    # load our Model
    import os
    TARGET_FILE = "model.pkl"
    list_of_files = [os.path.join(dirpath,filename) for dirpath, _, filenames in os.walk('.') for filename in filenames if filename == TARGET_FILE]

    if list_of_files:
        model_path = list_of_files[0]
        model = joblib.load(model_path)
    else:
        if not os.path.exists(TARGET_FILE):
            mr = project.get_model_registry()
            EVALUATION_METRIC="r2_score"  # or r2_score
            SORT_METRICS_BY="max"
            # get best model based on custom metrics
            model = mr.get_best_model("MLPRegressor",
                                      EVALUATION_METRIC,
                                      SORT_METRICS_BY)
            model_dir = model.download()
            model = joblib.load(model_dir + "/model.pkl")

    return model
