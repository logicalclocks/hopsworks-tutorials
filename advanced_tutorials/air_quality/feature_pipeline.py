import datetime
import time
import requests
import pandas as pd
import json
import hopsworks

from functions import *

import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

import os

# Get the value of the PARAMETER environment variable
continent = os.environ.get('CONTINENT')


file_path = os.path.join(os.getcwd(), 'advanced_tutorials', 'air_quality', 'target_cities.json')
with open(file_path) as json_file:
    target_cities = json.load(json_file)


def get_batch_data_from_fs(td_version, date_threshold):
    print(f"Retrieving the Batch data since {date_threshold}")
    feature_view.init_batch_scoring(training_dataset_version=td_version)

    batch_data = feature_view.get_batch_data(start_time=date_threshold)
    return batch_data


def parse_aq_data(last_dates_dict, today):
    start_of_cell = time.time()
    df_aq_raw = pd.DataFrame()
    
    print("Parsing started...")
    # for continent in target_cities:
    for city_name, coords in target_cities[continent].items():
        df_ = get_aqi_data_from_open_meteo(city_name=city_name,
                                           coordinates=coords,
                                           start_date=last_dates_dict[city_name],
                                           end_date=str(today))
        df_aq_raw = pd.concat([df_aq_raw, df_]).reset_index(drop=True)
    end_of_cell = time.time()
    print("-" * 64)
    print(f"Parsed new PM2.5 data for ALL locations up to {str(today)}.")
    print(f"Took {round(end_of_cell - start_of_cell, 2)} sec.\n")
    return df_aq_raw


def parse_weather(last_dates_dict, today):
    df_weather_update = pd.DataFrame()
    start_of_cell = time.time()
    
    print("Parsing started...")
    # for continent in target_cities:
    for city_name, coords in target_cities[continent].items():
        df_ = get_weather_data_from_open_meteo(city_name=city_name,
                                               coordinates=coords,
                                               start_date=last_dates_dict[city_name],
                                               end_date=str(today),
                                               forecast=True)
        df_weather_update = pd.concat([df_weather_update, df_]).reset_index(drop=True)

    end_of_cell = time.time()
    print(f"Parsed new weather data for ALL cities up to {str(today)}.")
    print(f"Took {round(end_of_cell - start_of_cell, 2)} sec.\n")
    return df_weather_update



if __name__=="__main__":
    project = hopsworks.login()
    fs = project.get_feature_store()
    print("✅ Logged in successfully!")

    feature_view = fs.get_feature_view(
        name='air_quality_fv',
        version=1
    )

    # I am going to load data for of last 60 days (for feature engineering)
    today = datetime.date.today()
    date_threshold = today - datetime.timedelta(days=60)
    
    print("Getting the batch data...")
    batch_data = get_batch_data_from_fs(td_version=1,
                                        date_threshold=date_threshold)

    print("Retreived batch data.")


    last_dates_dict = batch_data[["date", "city_name"]].groupby("city_name").max()
    last_dates_dict.date = last_dates_dict.date.astype(str)
    # here is a dictionary with city names as keys and last updated date as values
    last_dates_dict = last_dates_dict.to_dict()["date"]  
    
    df_aq_raw = parse_aq_data(last_dates_dict, today)

    # we need the previous data to calculate aggregation functions
    df_aq_update = pd.concat([
        batch_data[df_aq_raw.columns],
        df_aq_raw
    ]).reset_index(drop=True)
    df_aq_update = df_aq_update.drop_duplicates(subset=['city_name', 'date'])

    print(df_aq_update.tail(7))

    print('\n🛠 Feature Engineering the PM2.5')

    ###
    df_aq_update['date'] = pd.to_datetime(df_aq_update['date'])
    feature_engineer_aq(df_aq_update)
    df_aq_update = df_aq_update.dropna()
    
    print(df_aq_update.groupby("city_name").max().tail(7))
    print("✅ Success!")
    ###

    print(3 * "-")
    print('\n🌤📆  Parsing Weather data')

    df_weather_update = parse_weather(last_dates_dict, today)
    print(df_weather_update.groupby("city_name").max().tail(7))
    print("✅ Successfully parsed!")

    df_aq_update.date = df_aq_update.date.astype(str)
    df_weather_update.date = df_weather_update.date.astype(str)
    
    print("Connecting to feature groups...")
    air_quality_fg = fs.get_or_create_feature_group(
        name = 'air_quality',
        version = 1
    )
    weather_fg = fs.get_or_create_feature_group(
        name = 'weather',
        version = 1
    )

    df_aq_update.date = pd.to_datetime(df_aq_update.date)
    df_weather_update.date = pd.to_datetime(df_weather_update.date)

    df_aq_update["unix_time"] = df_aq_update["date"].apply(convert_date_to_unix)
    df_weather_update["unix_time"] = df_weather_update["date"].apply(convert_date_to_unix)

    df_aq_update.date = df_aq_update.date.astype(str)
    df_weather_update.date = df_weather_update.date.astype(str)

    air_quality_fg.insert(df_aq_update,
                          write_options={'wait_for_job': False})
    print("Created job to insert parsed PM2.5 data into FS...")
    print("Inserting into air_quality fg.")

    weather_fg.insert(df_weather_update,
                      write_options={'wait_for_job': False})
    print("Created job to insert parsed weather data into FS...")
    print("Inserting into weather fg.")