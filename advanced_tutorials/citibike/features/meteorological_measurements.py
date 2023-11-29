import pandas as pd
import os
from datetime import datetime

def convert_date_to_unix(x: str) -> int:
    """
    Convert a date string to Unix timestamp in milliseconds.

    Args:
        x (str): Date string in the format '%Y-%m-%d'.

    Returns:
        int: Unix timestamp in milliseconds.
    """
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)

def parse_weather_data(city: str, start_date: str, end_date: str, API_KEY: str) -> pd.DataFrame:
    """
    Parse weather data from Visual Crossing Weather API.

    Args:
        city (str): City name for weather data.
        start_date (str): Start date for weather data retrieval (format: 'YYYY-MM-DD').
        end_date (str): End date for weather data retrieval (format: 'YYYY-MM-DD').
        API_KEY (str): API key for accessing Visual Crossing Weather API.

    Returns:
        pd.DataFrame: Weather data DataFrame.
    """
    # yyyy-MM-DD data format
    formatted_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{start_date}/{end_date}?unitGroup=metric&include=days&key={API_KEY}&contentType=csv"
    return pd.read_csv(formatted_url)

def get_weather_data(city: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get weather data for a specific city and date range.

    Args:
        city (str): City name for weather data.
        start_date (str): Start date for weather data retrieval (format: 'YYYY-MM-DD').
        end_date (str): End date for weather data retrieval (format: 'YYYY-MM-DD').

    Returns:
        pd.DataFrame: Weather data DataFrame.
    """
    API_KEY = os.getenv("WEATHER_API_KEY")
    # API_KEY = ""

    df_res = parse_weather_data(city, start_date, end_date, API_KEY)
    # Drop redundant columns
    df_res = df_res.drop(
        columns=[
            "name", "icon", "stations", "description",
            "sunrise", "sunset", "preciptype",
            "severerisk", "conditions", "moonphase",
            "cloudcover", "sealevelpressure",
            "solarradiation", "winddir", "windgust",
            "uvindex", "solarenergy",
        ])

    df_res = df_res.rename(columns={"datetime": "date"})

    return df_res