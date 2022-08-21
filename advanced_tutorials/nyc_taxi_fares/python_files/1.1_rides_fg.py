#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd

import secrets

import hopsworks


# In[2]:


project = hopsworks.login()
fs = project.get_feature_store()


# In[3]:


cols = ['ride_id',
        'pickup_datetime',
        'pickup_longitude',
        'pickup_latitude',
        'dropoff_longitude',
        'dropoff_latitude',
        'passenger_count',
        'taxi_id',
        'driver_id']


# In[4]:


secrets.token_hex(nbytes=16)


# In[5]:


def generate_rides_data(n_records):
    res = pd.DataFrame(columns=cols)

    for i in range(1, n_records + 1):
        generated_values = list()


        temp_df = pd.DataFrame.from_dict({"ride_id": [secrets.token_hex(nbytes=16)],
                                          "pickup_datetime": [np.random.randint(1600000000, 1610000000)],
                                          "pickup_longitude": [round(np.random.uniform(-74.5, -72.8), 5)],
                                          "dropoff_longitude": [round(np.random.uniform(-74.5, -72.8), 5)],
                                          "pickup_latitude": [round(np.random.uniform(40.5, 41.8), 5)],
                                          "dropoff_latitude": [round(np.random.uniform(40.5, 41.8), 5)],
                                          "passenger_count": [np.random.randint(1, 5)],
                                          "taxi_id": [np.random.randint(1, 201)],
                                          "driver_id": [np.random.randint(1, 201)]
                                         })

        res = pd.concat([temp_df, res], ignore_index=True)

    return res


# In[6]:


df_rides = generate_rides_data(100)


# In[7]:


# returns distance in miles
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295 # Pi/180
    a = 0.5 - np.cos((lat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 0.6213712 * 12742 * np.arcsin(np.sqrt(a))


# In[8]:


df_rides["distance"] = distance(df_rides["pickup_latitude"], df_rides["pickup_longitude"],
                            df_rides["dropoff_latitude"], df_rides["dropoff_longitude"])


# In[9]:


# Distances to nearby airports
jfk = (-73.7781, 40.6413)
ewr = (-74.1745, 40.6895)
lgr = (-73.8740, 40.7769)

df_rides['pickup_distance_to_jfk'] = distance(jfk[1], jfk[0],
                                     df_rides['pickup_latitude'], df_rides['pickup_longitude'])
df_rides['dropoff_distance_to_jfk'] = distance(jfk[1], jfk[0],
                                       df_rides['dropoff_latitude'], df_rides['dropoff_longitude'])
df_rides['pickup_distance_to_ewr'] = distance(ewr[1], ewr[0],
                                      df_rides['pickup_latitude'], df_rides['pickup_longitude'])
df_rides['dropoff_distance_to_ewr'] = distance(ewr[1], ewr[0],
                                       df_rides['dropoff_latitude'], df_rides['dropoff_longitude'])
df_rides['pickup_distance_to_lgr'] = distance(lgr[1], lgr[0],
                                      df_rides['pickup_latitude'], df_rides['pickup_longitude'])
df_rides['dropoff_distance_to_lgr'] = distance(lgr[1], lgr[0],
                                       df_rides['dropoff_latitude'], df_rides['dropoff_longitude'])


# In[10]:


df_rides["pickup_datetime"] = (pd.to_datetime(df_rides["pickup_datetime"],unit='ms'))


# In[11]:


df_rides['year'] = df_rides.pickup_datetime.apply(lambda t: t.year)
df_rides['weekday'] = df_rides.pickup_datetime.apply(lambda t: t.weekday())
df_rides['hour'] = df_rides.pickup_datetime.apply(lambda t: t.hour)


# In[12]:


df_rides["pickup_datetime"] = df_rides["pickup_datetime"].values.astype(np.int64) // 10 ** 6


# ## <span style="color:#ff5f27;"> ⚖️ Great Expectations </span>
#
# Great Expectations’ built-in library includes more than 50 common Expectations, such as:
#
#     expect_column_values_to_not_be_null
#
#     expect_column_values_to_be_unique
#
#     expect_column_median_to_be_between...
#
# #### You can find more expectations in the [official docs](https://greatexpectations.io/expectations/)
#
#
# Clean, high quality feature data is of paramount importance to being able to train and serve high quality models. Hopsworks offers integration with [Great Expectations](https://greatexpectations.io/) to enable a smooth data validation workflow.
#
# ### `More info` - [here](https://docs.hopsworks.ai/3.0/user_guides/fs/feature_group/data_validation/)

# In[13]:


import great_expectations as ge

# Create (or import an existing) expectation suite using the Great Expectations library.
expectation_suite = ge.core.ExpectationSuite(
    expectation_suite_name="validate_on_insert_suite"
)


# In[14]:


# lets add an expecation to the 'total_fare' column
expectation_suite.add_expectation(
    ge.core.ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={
            "column": "pickup_longitude",
            "min_value": -74.5,
            "max_value": -72.8
        }
    )
)

# you can add as many expectations (to the different columns in the same time) as you want

expectation_suite.add_expectation(
    ge.core.ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={
            "column": "pickup_latitude",
            "min_value": 40.5,
            "max_value": 41.8
        }
    )
)


# In[15]:


# Using Great Expectations Profiler

ge_profiler = ge.profile.BasicSuiteBuilderProfiler()
expectation_suite_profiler, _ = ge_profiler.profile(ge.from_pandas(df_rides)) # here we pass a DataFrame to validate


# In[16]:


for col in ["passenger_count", "taxi_id", "driver_id"]:
    df_rides[col] = df_rides[col].astype("int32")


# In[17]:


rides_fg = fs.get_or_create_feature_group(name="rides_fg",
                                          version=1,
                                          primary_key=["ride_id"],
                                          event_time=["pickup_datetime"],
                                          partition_key=["month_of_the_ride"],
                                          expectation_suite=expectation_suite,
                                          description="Rides features",
                                          time_travel_format="HUDI",
                                          online_enabled=True,
                                          statistics_config=True)
rides_fg.insert(df_rides)


# In[18]:


# lets save our newly-generated ride_ids to the csv so
# we will retrieve them and use in fares_fg in the next notebook
df_rides.ride_id.to_csv("new_ride_ids.csv")
