#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import hopsworks


# In[2]:


project = hopsworks.login()
fs = project.get_feature_store()


# In[3]:


cols = ['taxi_id', 'driver_id',
       'tip', 'tolls', 'total_fare']


# In[4]:


def generate_fares_data(n_records):
    res = pd.DataFrame(columns=cols)
    
    for i in range(1, n_records + 1):
        generated_values = list()
     
        
        temp_df = pd.DataFrame.from_dict({"total_fare": [np.random.randint(3, 250)],
                                          "tip": [np.random.randint(0, 60)],
                                          "tolls": [np.random.randint(0, 6)],
                                          "taxi_id": [np.random.randint(1, 201)],
                                          "driver_id": [np.random.randint(1, 201)]
                                         })
        
        res = pd.concat([temp_df, res], ignore_index=True)
        
        
    return res


# In[5]:


df_fares = generate_fares_data(100)


# In[6]:


print(df_fares.head(5))


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

# In[7]:


import great_expectations as ge

# Create (or import an existing) expectation suite using the Great Expectations library.
expectation_suite = ge.core.ExpectationSuite(
    expectation_suite_name="validate_on_insert_suite"
)


# In[8]:


# lets add an expecation to the 'total_fare' column
expectation_suite.add_expectation(
    ge.core.ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={
            "column": "total_fare",
            "min_value": 3, 
            "max_value": 5000
        }
    )
)


# In[9]:


# Using Great Expectations Profiler

ge_profiler = ge.profile.BasicSuiteBuilderProfiler()
expectation_suite_profiler, _ = ge_profiler.profile(ge.from_pandas(df_fares)) # here we pass a DataFrame to validate


# In[10]:


df_fares = df_fares.astype("int64")


# In[11]:


# lets load our ride_ids which were created moments ago for rides_fg
df_fares["ride_id"] = pd.read_csv("new_ride_ids.csv")["ride_id"]


# In[12]:


for col in ["tip", "tolls", "total_fare"]:
    df_fares[col] = df_fares[col].astype("double")


# In[13]:


fares_fg = fs.get_or_create_feature_group(name="fares_fg",
                                          version=1,
                                          primary_key=["ride_id"], 
                                          description="Taxi fares features",
                                          expectation_suite=expectation_suite,
                                          time_travel_format="HUDI",  
                                          online_enabled=True,
                                          statistics_config=True)   
fares_fg.insert(df_fares)

