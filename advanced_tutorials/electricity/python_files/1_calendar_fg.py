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
    df[['holiday','school_day']] = df[['holiday','school_day']].apply(lambda x: x.map({'Y': 1, 'N': 0}))
    if type(df.date[0]) != np.int64:
        df.date = df.date.apply(lambda x: timestamp_2_time(str(x)[:19])).astype(np.int64)
    return df


def create_feature_group(data = None,name='calendar_fg',fs=fs):
    import great_expectations as ge
    
    expectation_suite = ge.core.ExpectationSuite(
        expectation_suite_name="Expectation Suite for Calendar Feature Group"
    )

    expectation = ge.core.ExpectationConfiguration(
       expectation_type="expect_column_value_lengths_to_be_between",
       kwargs={
          "column": "school_day",
          "min_value": 1,
           "max_value": 1,
       },
        meta={
          "notes": {
             "format": "markdown",
             "content": "Possible values for `holiday` column are **Y** and **No**. *Meaning*: is a specific day a holiday or not."
          }
       }
    )

    expectation_suite.add_expectation(expectation)
    
    feature_group = fs.get_or_create_feature_group(
        name=name,
        description = 'Characteristics of each day',
        version = 1,
        primary_key = ['index'],
        online_enabled = True,
        event_time = ['date'],
        expectation_suite=expectation_suite
    )
        
    feature_group.insert(data.reset_index())
    
    return feature_group


def retrieve_feature_group(name='calendar_fg',fs=fs):
    feature_group = fs.get_feature_group(
        name=name,
        version=1
    )
    return feature_group


try:
    feature_group = retrieve_feature_group()
    df_calendar = feature_group.read()
    indexes = df_calendar.pop('index')
    
except: 
    DATA_PATH = './data/calendar.csv'
    
    df_calendar = get_data(DATA_PATH)
    feature_engineering(df_calendar)
    
    feature_group = create_feature_group(df_calendar)

df_calendar.head()



date_window = 24*60*60*1000


def generate_observation(columns):
    return [random.choice(['Y','N'],) for col in columns[1:]]

def generate_data(df,amount = 1,date_window = date_window):
    df_last = df.sort_values('date').date.iloc[-1]
    df_generated = pd.DataFrame(columns = ['date',*df.columns[1:]])
    for i in range(1, amount + 1):
        df_generated.loc[len(df_generated)] = [df_last + date_window * i,*generate_observation(df.columns)]
    return df_generated.astype({'date':int})

def append_generated_data(df,amount = 1,date_window = date_window):
    df_last = df.sort_values('date').date.iloc[-1]
    for i in range(1, amount + 1):
        df.loc[len(df)] = [df_last + date_window,*generate_observation(df.columns)]
    return df


def add_indexes(df,indexes=None):
    if indexes is None:
        return df.reset_index()
    df.reset_index(inplace = True)
    df['index'] = df['index'] + indexes.max() + 1
    return df


generated_data = generate_data(df_calendar,50)
feature_engineering(generated_data)

try: 
    generated_data = add_indexes(generated_data,indexes)
except:
    generated_data = add_indexes(generated_data)

generated_data.head()


feature_group.insert(generated_data)

print('🎉 🤝 Calendar Feature Group is Ready! 🤝 🎉')

