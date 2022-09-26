import pandas as pd
from datetime import datetime
import requests


def get_air_json(city_name,API_KEY):
    return requests.get(f'https://api.waqi.info/feed/{city_name}/?token={API_KEY}').json()['data']


def get_air_quality_data(city_name,API_KEY):
    json = get_air_json(city_name,API_KEY)
    iaqi = json['iaqi']
    forecast = json['forecast']['daily']
    return [
        city_name,
        json['aqi'],                 # AQI 
        json['time']['s'][:10],      # Date
        iaqi['h']['v'],
        iaqi['p']['v'],
        iaqi['pm10']['v'],
        iaqi['t']['v'],
        forecast['o3'][0]['avg'],
        forecast['o3'][0]['max'],
        forecast['o3'][0]['min'],
        forecast['pm10'][0]['avg'],
        forecast['pm10'][0]['max'],
        forecast['pm10'][0]['min'],
        forecast['pm25'][0]['avg'],
        forecast['pm25'][0]['max'],
        forecast['pm25'][0]['min'],
        forecast['uvi'][0]['avg'],
        forecast['uvi'][0]['avg'],
        forecast['uvi'][0]['avg']
    ]

def get_air_quality_df(data):
    col_names = [
        'city',
        'aqi',
        'date',
        'iaqi_h',
        'iaqi_p',
        'iaqi_pm10',
        'iaqi_t',
        'o3_avg',
        'o3_max',
        'o3_min',
        'pm10_avg',
        'pm10_max',
        'pm10_min',
        'pm25_avg',
        'pm25_max',
        'pm25_min',  
        'uvi_avg',
        'uvi_max',
        'uvi_min', 
    ]

    new_data = pd.DataFrame(
        data,
        columns=col_names
    )
    new_data.date = new_data.date.apply(timestamp_2_time)

    return new_data


def get_weather_json(city, date, API_KEY):
    return requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city.lower()}/{date}?unitGroup=metric&include=days&key={API_KEY}&contentType=json').json()


def get_weather_data(city_name,date,API_KEY):
    json = get_weather_json(city_name,date,API_KEY)
    data = json['days'][0]
    
    return [
        json['address'].capitalize(),
        data['datetime'],
        data['tempmax'],
        data['tempmin'],
        data['temp'],
        data['feelslikemax'],
        data['feelslikemin'],
        data['feelslike'],
        data['dew'],
        data['humidity'],
        data['precip'],
        data['precipprob'],
        data['precipcover'],
        data['snow'],
        data['snowdepth'],
        data['windgust'],
        data['windspeed'],
        data['winddir'],
        data['pressure'],
        data['cloudcover'],
        data['visibility'],
        data['solarradiation'],
        data['solarenergy'],
        data['uvindex'],
        data['conditions']
    ]


def get_weather_df(data):
    col_names = [
        'city',
        'date',
        'tempmax',
        'tempmin',
        'temp',
        'feelslikemax',
        'feelslikemin',
        'feelslike',
        'dew',
        'humidity',
        'precip',
        'precipprob',
        'precipcover',
        'snow',
        'snowdepth',
        'windgust',
        'windspeed',  
        'winddir',
        'pressure',
        'cloudcover', 
        'visibility',
        'solarradiation',
        'solarenergy',
        'uvindex',
        'conditions'
    ]

    new_data = pd.DataFrame(
        data,
        columns=col_names
    )
    new_data.date = new_data.date.apply(timestamp_2_time)

    return new_data

def timestamp_2_time(x):
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)