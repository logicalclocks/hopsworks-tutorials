from datetime import datetime
import requests
import os
import joblib
import pandas as pd

from dotenv import load_dotenv
load_dotenv()


def decode_features(df, feature_view):
    """Decodes features in the input DataFrame using corresponding Hopsworks Feature Store transformation functions"""
    df_res = df.copy()

    import inspect


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


def get_model(project, model_name, evaluation_metric, sort_metrics_by):
    """Retrieve desired model or download it from the Hopsworks Model Registry.

    In second case, it will be physically downloaded to this directory"""
    TARGET_FILE = "model.pkl"
    list_of_files = [os.path.join(dirpath,filename) for dirpath, _, filenames \
                     in os.walk('.') for filename in filenames if filename == TARGET_FILE]

    if list_of_files:
        model_path = list_of_files[0]
        model = joblib.load(model_path)
    else:
        if not os.path.exists(TARGET_FILE):
            mr = project.get_model_registry()
            # get best model based on custom metrics
            model = mr.get_best_model(model_name,
                                      evaluation_metric,
                                      sort_metrics_by)
            model_dir = model.download()
            model = joblib.load(model_dir + "/model.pkl")

    return model


def get_air_json(city_name, AIR_QUALITY_API_KEY):
    return requests.get(f'https://api.waqi.info/feed/{city_name}/?token={AIR_QUALITY_API_KEY}').json()['data']


def get_air_quality_data(city_name):
    AIR_QUALITY_API_KEY = os.getenv('AIR_QUALITY_API_KEY')
    json = get_air_json(city_name, AIR_QUALITY_API_KEY)
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


def get_weather_json(city, date, WEATHER_API_KEY):
    return requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city.lower()}/{date}?unitGroup=metric&include=days&key={WEATHER_API_KEY}&contentType=json').json()


def get_weather_data(city_name, date):
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    json = get_weather_json(city_name, date, WEATHER_API_KEY)
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
