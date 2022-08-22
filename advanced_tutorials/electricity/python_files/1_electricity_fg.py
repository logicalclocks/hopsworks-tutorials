#!/usr/bin/env python
# coding: utf-8

# 
# 
# # <span style="color:#ff5f27;"> 🧑🏻‍🏫 Great Expectations </span>
# 
# 
# Great Expectations is the leading tool for validating, documenting, and profiling your data to maintain quality and improve communication between teams. Head over to our getting started tutorial.
# 
# Software developers have long known that automated testing is essential for managing complex codebases. Great Expectations brings the same discipline, confidence, and acceleration to data science and data engineering teams.
# 
# With Great Expectations, you can assert what you expect from the data you load and transform, and catch data issues quickly – Expectations are basically unit tests for your data. Not only that, but Great Expectations also creates data documentation and data quality reports from those Expectations.
# 
# To begin with, let's install `great_expectations` library.

# In[1]:


#!pip install great_expectations -U -qqq


# Then - import `great_expectations` library and define `ExpectationSuite`
# 
# - `Expectations` are the workhorse abstraction in Great Expectations. Each Expectation is a declarative, machine-verifiable assertion about the expected format, content, or behavior of your data. Great Expectations comes with dozens of built-in Expectations, and it’s possible to develop your own custom Expectations, too.
# 
# - `ExpectationSuite` - a collection of `Expectations` about data which you will use when you **Validate** data.
# 
# Then create `Expectations`.
# 
# You can create them using `ge.core.ExpectationConfiguration()` function with next parameters:
# 
# - **expectation_type** - specify the [name of expectations](https://greatexpectations.io/expectations/) you need.
# 
# - **kwargs** - specify keyword arguments of this Expectation Type.
# 
# Then you should add some expectation to your suite to validate columns.
# 
# You can do it by using `expectation_suite.add_expectation()` method.

# ## <span style="color:#ff5f27;"> 📝 Imports</span>

# In[2]:


import pandas as pd
import numpy as np
import random
from datetime import datetime

# import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')


# In[3]:


# from hops import hdfs

# project_path = hdfs.project_path()

# project_path


# ## <span style="color:#ff5f27;"> 🔮 Connecting to Hopsworks Feature Store </span>

# In[4]:


import hopsworks

project = hopsworks.login()

fs = project.get_feature_store() 


# ## <span style="color:#ff5f27;">🧑🏻‍🏫 Functions</span>

# In[5]:


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
    windows = [7,14,30]
    for window in windows:
        df[f'demand_{window}_mean'] = df.demand.rolling(window = window).mean()
        df[f'demand_{window}_std'] = df.demand.rolling(window = window).std()
    if type(df.date[0]) != np.int64:
        df.date = df.date.apply(lambda x: timestamp_2_time(str(x)[:19])).astype(np.int64)
    df.dropna(inplace=True)
    return df


def create_feature_group(data = None,name='electricity_fg',fs=fs):
    import great_expectations as ge
    
    expectation_suite = ge.core.ExpectationSuite(
        expectation_suite_name="Expectation Suite for Electricity Feature Group"
    )
    expectation = ge.core.ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={
             "column": "date",
             "mostly": 1.0
         }
    )
    expectation_suite.add_expectation(expectation)
    
    feature_group = fs.get_or_create_feature_group(
        name=name,
        description = 'Daily Electricity Price and Demand',
        version = 1,
        primary_key = ['index'],
        online_enabled = True,
        event_time = ['date'],
        expectation_suite=expectation_suite
    )
        
    feature_group.insert(data.reset_index())
    
    return feature_group


def retrieve_feature_group(name='electricity_fg',fs=fs):
    feature_group = fs.get_feature_group(
        name=name,
        version=1
    )
    return feature_group


# ## <span style="color:#ff5f27;">🪄 👩🏻‍🔬 Retrieving or Creating Feature Group</span>

# In[6]:


try:
    feature_group = retrieve_feature_group()
    df_electricity = feature_group.read()
    df_electricity.sort_values('date',inplace=True)
    indexes = df_electricity.pop('index')
    
except: 
    DATA_PATH = project_path + 'Jupyter/data/electricity.csv'
    
    df_electricity = get_data(DATA_PATH)
    feature_engineering(df_electricity)
    
    feature_group = create_feature_group(df_electricity)


# In[7]:


df_electricity.head()


# ## <span style="color:#ff5f27;">🕵🏻‍♂️ Data Exploration</span>

# In[8]:


# fig,ax = plt.subplots(figsize = (16,6))

# df_electricity.plot('date','demand', ax = ax)

# ax.set_xlabel('Date',fontsize = 15)
# ax.set_ylabel('Demand MWh',fontsize = 15)
# ax.set_title('Daily electricity demand from January 2015 to October 2020',fontsize = 20)

# plt.show()


# In[9]:


# fig,ax = plt.subplots(figsize = (16,6))

# try:
#     df_electricity.plot('date','RRP', ax = ax)
# except:
#     df_electricity.plot('date','rrp', ax = ax)
    
# ax.set_xlabel('Date',fontsize = 15)
# ax.set_ylabel('Price in AUD$/MWh',fontsize = 15)
# ax.set_title('Daily price in AUD$/MWh from January 2015 to October 2020',fontsize = 20)

# plt.yscale("log")
# plt.show()


# ## <span style="color:#ff5f27;">🧬 Data Generation</span>

# In[10]:


def get_statistics(feature):
    mean = feature.mean()
    lower_value,upper_value = mean - feature.std() * 3,mean + feature.std() * 3
    return lower_value,upper_value


# In[11]:


statistics = {col:get_statistics(df_electricity[col]) for col in df_electricity.columns[1:]}

date_window = 24*60*60*1000


# In[12]:


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


# In[13]:


append_generated_data(df_electricity,50)

df_electricity.tail()


# ## <span style="color:#ff5f27;">👩🏻‍⚖️ 🪄 Validation and Insertion of Generated Data</span>

# In[14]:


def add_indexes(df,indexes=None):
    if indexes is None:
        return df.reset_index()
    df.reset_index(inplace = True)
    df['index'] = df['index'] + indexes.max() + 1
    return df


# In[15]:


generated_data = generate_data(df_electricity,50)
feature_engineering(generated_data)

try: 
    generated_data = add_indexes(generated_data,indexes)
except:
    generated_data = add_indexes(generated_data)

generated_data.head()


# In[16]:


feature_group.insert(generated_data)

