import time
from functions.common_functions import *
import requests
import pandas as pd


def get_weather_data_from_open_meteo(
    city_name: str,
    start_date: str,
    end_date: str,
    coordinates: list = None,
    forecast: bool = False,
    ):
    """
    Takes [city name OR coordinates] and returns pandas DataFrame with weather data.
    
    Examples of arguments:
        coordinates=(47.755, -122.2806), start_date="2023-01-01"
    """
    start_of_cell = time.time()
    
    if coordinates:
        latitude, longitude = coordinates
    else:
        latitude, longitude = get_city_coordinates(city_name=city_name)
    
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'daily': ["temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "rain_sum", "snowfall_sum",
                "precipitation_hours", "windspeed_10m_max",
                "windgusts_10m_max", "winddirection_10m_dominant"],
        'timezone': "Europe/London",
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if forecast:
        # historical forecast endpoint
        base_url = 'https://api.open-meteo.com/v1/forecast' 
    else:
        # historical observations endpoint
        base_url = 'https://archive-api.open-meteo.com/v1/archive'  
        
    try:
        response = requests.get(base_url, params=params)
        time.sleep(2)
    except ConnectionError:
        response = requests.get(base_url, params=params)
    
    response_json = response.json()    

    res_df = pd.DataFrame(response_json["daily"])  
    res_df["city_name"] = city_name
    
    # rename columns
    res_df = res_df.rename(columns={
        "time": "date",
        "temperature_2m_max": "temperature_max",
        "temperature_2m_min": "temperature_min",
        "windspeed_10m_max": "wind_speed_max",
        "winddirection_10m_dominant": "wind_direction_dominant",
        "windgusts_10m_max": "wind_gusts_max"
    })
    
    # change columns order
    res_df = res_df[
        ['city_name', 'date', 'temperature_max', 'temperature_min',
         'precipitation_sum', 'rain_sum', 'snowfall_sum',
         'precipitation_hours', 'wind_speed_max',
         'wind_gusts_max', 'wind_direction_dominant']
    ]
    
    # convert dates in 'date' column
    res_df["date"] = pd.to_datetime(res_df["date"])
    end_of_cell = time.time()
    print(f"Parsed weather for {city_name} since {start_date} till {end_date}.")
    print(f"Took {round(end_of_cell - start_of_cell, 2)} sec.\n")
        
    return res_df