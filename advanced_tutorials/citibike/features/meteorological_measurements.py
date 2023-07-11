import pandas as pd
import os
from datetime import datetime


def convert_date_to_unix(x):
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


def parse_weather_data(city, start_date, end_date, API_KEY):
    # yyyy-MM-DD data format
    formatted_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{start_date}/{end_date}?unitGroup=metric&include=days&key={API_KEY}&contentType=csv"
    return pd.read_csv(formatted_url)


def get_weather_data(city, start_date, end_date):
    API_KEY = os.getenv("WEATHER_API_KEY")
    # API_KEY = ""

    df_res = parse_weather_data(city, start_date, end_date, API_KEY)
    # drop redundant columns
    df_res = df_res.drop(columns=["name", "icon", "stations", "description",
                                  "sunrise", "sunset", "preciptype",
                                  "severerisk", "conditions", "moonphase",
                                  "cloudcover", "sealevelpressure",
                                  "solarradiation", "winddir", "windgust",
                                  "uvindex", "solarenergy"])

    df_res = df_res.rename(columns={"datetime": "date"})

    return df_res