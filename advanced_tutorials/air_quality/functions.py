import os
import datetime
import time
import requests
import pandas as pd
import json

from geopy.geocoders import Nominatim


def convert_date_to_unix(x):
    """
    Convert datetime to unix time in milliseconds.
    """
    dt_obj = datetime.datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    dt_obj = int(dt_obj.timestamp() * 1000)
    return dt_obj


def get_city_coordinates(city_name: str):
    """
    Takes city name and returns its latitude and longitude (rounded to 2 digits after dot).
    """ 
    # Initialize Nominatim API (for getting lat and long of the city)
    geolocator = Nominatim(user_agent="MyApp")
    city = geolocator.geocode(city_name)

    latitude = round(city.latitude, 2)
    longitude = round(city.longitude, 2)
    
    return latitude, longitude


##################################### EEA
def convert_to_daily(df, pollutant: str):
    """
    Returns DataFrame where pollutant column is resampled to days and rounded.
    """
    res_df = df.copy()
    # convert dates in 'time' column
    res_df["date"] = pd.to_datetime(res_df["date"])
    
    # I want data daily, not hourly (mean per each day = 1 datarow per 1 day)
    res_df = res_df.set_index('date')
    res_df = res_df[pollutant].resample('1d').mean().reset_index()
    res_df[pollutant] = res_df[pollutant].fillna(res_df[pollutant].median())
    res_df[pollutant] = res_df[pollutant].apply(lambda x: round(x, 0))
    
    return res_df


def find_fullest_csv(csv_links: list, year: str):
    candidates = [link for link in csv_links if str(year) in link]
    biggest_df = pd.read_csv(candidates[0])
    for link in candidates[1:]:
        _df = pd.read_csv(link)
        if len(biggest_df) < len(_df):
            biggest_df = _df
    return biggest_df


def get_air_quality_from_eea(city_name: str,
                             pollutant: str,
                             start_year: str,
                             end_year: str):
    """
    Takes city name, daterange and returns pandas DataFrame with daily air quality data.
    It parses data by 1-year batches, so please specify years, not dates. (example: "2014", "2022"...)
    
    EEA means European Environmental Agency. So it has data for Europe Union countries ONLY.
    """
    start_of_cell = time.time()
    
    params = {
        'CountryCode': '',
        'CityName': city_name,
        'Pollutant': pollutant.upper(),
        'Year_from': start_year,
        'Year_to': end_year,
        'Station': '',
        'Source': 'All',
        'Samplingpoint': '',
        'Output': 'TEXT',
        'UpdateDate': '',
        'TimeCoverage': 'Year'
    }

    # observations endpoint
    base_url = "https://fme.discomap.eea.europa.eu/fmedatastreaming/AirQualityDownload/AQData_Extract.fmw?"
    try:
        response = requests.get(base_url, params=params)
    except ConnectionError:
        response = requests.get(base_url, params=params)
        
    response.encoding = response.apparent_encoding
    csv_links = response.text.split("\r\n")
    
    res_df = pd.DataFrame()
    target_year = int(start_year)
    
    for year in range(int(start_year), int(end_year) + 1):
        try:
            # find the fullest, the biggest csv file with observations for this particular year
            _df = find_fullest_csv(csv_links, year)
            # append it to res_df
            res_df = pd.concat([res_df, _df])
        except IndexError:
            print(f"!! Missing data for {year} for {city} city.")
            pass
        
    pollutant = pollutant.lower()
    if pollutant == "pm2.5":
        pollutant = "pm2_5"
        
    res_df = res_df.rename(columns={
        'DatetimeBegin': 'date',
        'Concentration': pollutant        
    })
    
    # cut timezones info
    res_df['date'] = res_df['date'].apply(lambda x: x[:-6])
    # convert dates in 'time' column
    res_df['date'] = pd.to_datetime(res_df['date'])
    
    res_df = convert_to_daily(res_df, pollutant)
    
    res_df['city_name'] = city_name
    res_df = res_df[['city_name', 'date', pollutant.lower()]]
    
    end_of_cell = time.time()
    
    print(f"Processed {pollutant.upper()} for {city_name} since {start_year} till {end_year}.")
    print(f"Took {round(end_of_cell - start_of_cell, 2)} sec.\n")
    
    return res_df



##################################### USEPA
city_code_dict = {}
pollutant_dict = {
    'CO': '42101',
    'SO2': '42401',
    'NO2': '42602',
    'O3': '44201',
    'PM10': '81102',
    'PM2.5': '88101'
}

def get_city_code(city_name: str):
    "Encodes city name to be used later for data parsing using USEPA."
    if city_code_dict:
        city_full = [i for i in city_code_dict.keys() if city_name in i][0]
        return city_code_dict[city_full]
    else:
        params = {
            "email": "test@aqs.api",
            "key": "test"
        }
        response = requests.get("https://aqs.epa.gov/data/api/list/cbsas?", params)
        response_json = response.json()
        data = response_json["Data"]
        for item in data:
            city_code_dict[item['value_represented']] = item['code']
        
        return get_city_code(city_name)

    
def get_air_quality_from_usepa(city_name: str,
                               pollutant: str,
                               start_date: str,
                               end_date: str):
    """
    Takes city name, daterange and returns pandas DataFrame with daily air quality data.
    
    USEPA means United States Environmental Protection Agency. So it has data for US ONLY.
    """
    start_of_cell = time.time()   
    res_df = pd.DataFrame()
    
    for start_date_, end_date_ in make_date_intervals(start_date, end_date):
        params = {
            "email": "test@aqs.api",
            "key": "test",
            "param": pollutant_dict[pollutant.upper().replace("_", ".")], # encoded pollutant 
            "bdate": start_date_,
            "edate": end_date_,
            "cbsa": get_city_code(city_name) # Core-based statistical area
        }

        # observations endpoint
        base_url = "https://aqs.epa.gov/data/api/dailyData/byCBSA?" 

        response = requests.get(base_url, params=params)
        response_json = response.json()
        
        df_ = pd.DataFrame(response_json["Data"])
        
        pollutant = pollutant.lower()      
        if pollutant == "pm2.5":
            pollutant = "pm2_5"
        df_ = df_.rename(columns={
            'date_local': 'date',
            'arithmetic_mean': pollutant        
        })

        # convert dates in 'date' column
        df_['date'] = pd.to_datetime(df_['date'])
        df_['city_name'] = city_name    
        df_ = df_[['city_name', 'date', pollutant]]
        res_df = pd.concat([res_df, df_])
    
    # there are duplicated rows (several records for the same day and station). get rid of it.
    res_df = res_df.groupby(['date', 'city_name'], as_index=False)[pollutant].mean()
    res_df[pollutant] = round(res_df[pollutant], 1)  
    
    end_of_cell = time.time()
    print(f"Processed {pollutant.upper()} for {city_name} since {start_date} till {end_date}.")
    print(f"Took {round(end_of_cell - start_of_cell, 2)} sec.\n")
    
    return res_df

    
def make_date_intervals(start_date, end_date):
    start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    date_intervals = []
    for year in range(start_dt.year, end_dt.year + 1):
        year_start = datetime.datetime(year, 1, 1)
        year_end = datetime.datetime(year, 12, 31)
        interval_start = max(start_dt, year_start)
        interval_end = min(end_dt, year_end)
        if interval_start < interval_end:
            date_intervals.append((interval_start.strftime('%Y%m%d'), interval_end.strftime('%Y%m%d')))
    return date_intervals

##################################### Weather Open Meteo
def get_weather_data_from_open_meteo(city_name: str,
                                     start_date: str,
                                     end_date: str,
                                     coordinates: list = None,
                                     forecast: bool = False):
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
        'start_date': start_date,
        'end_date': end_date,
        'timezone': "Europe/London"
    }
    
    if forecast:
        # historical forecast endpoint
        base_url = 'https://api.open-meteo.com/v1/forecast' 
    else:
        # historical observations endpoint
        base_url = 'https://archive-api.open-meteo.com/v1/archive'  
        
    try:
        response = requests.get(base_url, params=params)
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


##################################### Air Quality data from Open Meteo
def get_aqi_data_from_open_meteo(city_name: str,
                                 start_date: str,
                                 end_date: str,
                                 coordinates: list = None,
                                 pollutant: str = "pm2_5"):
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

