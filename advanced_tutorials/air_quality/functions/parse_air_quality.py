import time
from functions.common_functions import *
import requests
import pandas as pd


def get_aqi_data_from_open_meteo(
    city_name: str,
    start_date: str,
    end_date: str,
    coordinates: list = None,
    pollutant: str = "pm2_5"
    ):
    """
    Takes [city name OR coordinates] and returns pandas DataFrame with AQI data.
    
    Examples of arguments:
        ...
        coordinates=(47.755, -122.2806),
        start_date="2023-01-01",
        pollutant="no2"
        ...
    """
    start_of_cell = time.time()
    
    if coordinates:
        latitude, longitude = coordinates
    else:
        latitude, longitude = get_city_coordinates(city_name=city_name)
    
    pollutant = pollutant.lower()
    if pollutant == "pm2.5":
        pollutant = "pm2_5"
    
    # make it work with both "no2" and "nitrogen_dioxide" passed.
    if pollutant == "no2":
        pollutant = "nitrogen_dioxide"
        
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': [pollutant],
        'start_date': start_date,
        'end_date': end_date,
        'timezone': "Europe/London"
    }
    
    # base endpoint
    base_url = "https://air-quality-api.open-meteo.com/v1/air-quality"   
    try:
        response = requests.get(base_url, params=params)
    except ConnectionError:
        response = requests.get(base_url, params=params)
    response_json = response.json()    
    res_df = pd.DataFrame(response_json["hourly"])       
    
    # convert dates
    res_df["time"] = pd.to_datetime(res_df["time"])
    
    # resample to days
    res_df = res_df.groupby(res_df['time'].dt.date).mean(numeric_only=True).reset_index()
    res_df[pollutant] = round(res_df[pollutant], 1)
    
    # rename columns
    res_df = res_df.rename(columns={
        "time": "date"
    })
    
    res_df["city_name"] = city_name
    
    # change columns order
    res_df = res_df[
        ['city_name', 'date', pollutant]
    ]
    end_of_cell = time.time()
    print(f"Processed {pollutant.upper()} for {city_name} since {start_date} till {end_date}.")
    print(f"Took {round(end_of_cell - start_of_cell, 2)} sec.\n")
    
    return res_df