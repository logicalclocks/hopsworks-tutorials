import pandas as pd
import numpy as np
import random
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

import hopsworks


project = hopsworks.login()
fs = project.get_feature_store() 


def get_data(data_path):
    df = pd.read_csv(data_path,
        index_col = 0,
        parse_dates = ['date']
    ).dropna()
    
    return df    

def timestamp_2_time(x):
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    dt_obj = dt_obj.timestamp() * 1000
    return dt_obj

def to_date(unix):
    return datetime.utcfromtimestamp(unix / 1000).strftime('%Y-%m-%d %H:%M:%S')

def feature_engineering(df):
    if type(df.date[0]) == np.int64:
        df.date = pd.to_datetime(df.date.apply(to_date))
    df['day_of_week'] = df.date.dt.dayofweek
    df['day_of_month'] = df.date.dt.day
    df['day_of_year'] = df.date.dt.dayofyear
    df['week_of_year'] = df.date.dt.weekofyear
    df['month'] = df.date.dt.month
    df['quarter'] = df.date.dt.quarter
    df['year'] = df.date.dt.year
    df.date = df.date.apply(lambda x: timestamp_2_time(str(x)[:19])).astype(np.int64)
    
    return df


def create_feature_group(data = None,name='weather_fg',fs=fs):
    import great_expectations as ge
    
    expectation_suite = ge.core.ExpectationSuite(
        expectation_suite_name="Expectation Suite for Weather Feature Group"
    )
    
    expectation = ge.core.ExpectationConfiguration(
        expectation_type="expect_column_max_to_be_between",
        kwargs={
            "column": "min_temperature",
            "min_value": -30,
            "max_value": 30
        }
    )
    expectation_suite.add_expectation(expectation)
    
    feature_group = fs.get_or_create_feature_group(
        name=name,
        description = 'Daily weather conditions',
        version = 1,
        primary_key = ['index'],
        online_enabled = True,
        event_time = ['date'],
        expectation_suite=expectation_suite
    )
        
    feature_group.insert(data.reset_index())
    
    return feature_group


def retrieve_feature_group(name='weather_fg',fs=fs):
    feature_group = fs.get_feature_group(
        name=name,
        version=1
    )
    return feature_group



try:
    feature_group = retrieve_feature_group()
    df_weather = feature_group.read()
    indexes = df_weather.pop('index')
    
except: 
    DATA_PATH = './data/weather.csv'
    
    df_weather = get_data(DATA_PATH)
    feature_engineering(df_weather)
    
    feature_group = create_feature_group(df_weather)



df_weather.head()


def get_statistics(feature):
    mean = feature.mean()
    lower_value,upper_value = mean - feature.std() * 3,mean + feature.std() * 3
    return lower_value,upper_value


statistics = {col:get_statistics(df_weather[col]) for col in df_weather.columns[1:]}

date_window = 24*60*60*1000



def generate_observation(statistics):
    return [round(random.uniform(lower_value, upper_value),1) for lower_value, upper_value in statistics.values()]

def generate_data(df,amount = 1,date_window = date_window,statistics=statistics):
    df_last = df.sort_values('date').date.iloc[-1]
    df_generated = pd.DataFrame(columns = ['date',*statistics.keys()])
    for i in range(1, amount + 1):
        df_generated.loc[len(df_generated)] = [df_last + date_window * i,*generate_observation(statistics)]
    return df_generated.astype({'date':int})

def append_generated_data(df,amount = 1,date_window = date_window,statistics=statistics):
    df_last = df.sort_values('date').date.iloc[-1]
    for i in range(1, amount + 1):
        df.loc[len(df)] = [df_last + date_window,*generate_observation(statistics)]
    df.date = df.date.apply(int)
    return df


def add_indexes(df,indexes=None):
    if indexes is None:
        return df.reset_index()
    df.reset_index(inplace = True)
    df['index'] = df['index'] + indexes.max() + 1
    return df


generated_data = generate_data(df_weather,50)
feature_engineering(generated_data)

try: 
    generated_data = add_indexes(generated_data,indexes)
except:
    generated_data = add_indexes(generated_data)

generated_data.head()


feature_group.insert(generated_data)

print('🎉 🤝 Weather Feature Group is Ready! 🤝 🎉')