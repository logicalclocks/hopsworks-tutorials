#!/usr/bin/env python
# coding: utf-8

# # <span style="font-width:bold; font-size: 3rem; color:#1EB182;"><img src="images/icon102.png" width="38px"></img> **Hopsworks Feature Store** </span><span style="font-width:bold; font-size: 3rem; color:#333;">- Part 02: Training Data & Feature views</span>
# 
# <span style="font-width:bold; font-size: 1.4rem;">This is the second part of the quick start series of tutorials about Hopsworks Feature Store. This notebook explains how to read from a feature group and create training dataset within the feature store</span>
# 
# ## 🗒️ In this notebook we will see how to create a training dataset from the feature groups: 
# 
# 1. Retrieving Feature Groups
# 2. Feature Group investigation
# 3. Transformation functions
# 4. Feature Views
# 5. Training Datasets
# 6. Training Datasets with Event Time filter
# 
# 
# 
# ![tutorial-flow](images/02_training-dataset.png) 

# ---
# 
# ## <span style="color:#ff5f27;"> 🔮 🪝 Connecting to Feature Store and Retrieving Feature Groups </span>

# In[1]:


import hopsworks

project = hopsworks.login()

fs = project.get_feature_store() 


# > In order to retrieve necessary Feature Group we can use `FeatureStore.get_or_create_feature_group()` method.

# In[2]:


fg_weather = fs.get_or_create_feature_group(
    name = 'weather_fg',
    version = 1
)


# In[3]:


fg_calendar = fs.get_or_create_feature_group(
    name = 'calendar_fg',
    version = 1
)


# In[4]:


fg_electricity = fs.get_or_create_feature_group(
    name = 'electricity_fg',
    version = 1
)


# ---
# 
# # <span style="color:#ff5f27;">🕵🏻‍♂️ Feature Groups Investigation</span>

# We can use `FeatureGroup.show()` method to select top n rows. 
# 
# Also we use method `FeatureGroup.read()` in order **to aggregate queries**, which are the output of next methods:
# 
# - `FeatureGroup.get_feature()` to get specific feature from our Feature Group.
# 
# - `FeatureGroup.select()` to get a subset of features from our Feature Group.
# 
# - `FeatureGroup.select_all()` to get all features from our Feature Group.
# 
# - `FeatureGroup.select_except()` to get all features except a few from our Feature Group.
# 
# - `FeatureGroup.filter()` to apply specific filter to the feature group.

# In[5]:


fg_weather.select_all()


# In[6]:


fg_weather.select_all().read().head()


# In[7]:


fg_calendar.select_except(['index']).show(5)


# In[8]:


fg_electricity.select('demand').show(5)


# In[9]:


fg_electricity.filter(fg_electricity.demand > 10000).show(5)


# ---
# 
# # <span style="color:#ff5f27;">🧑🏻‍🔬 Transformation functions</span>

# Hopsworks Feature Store provides functionality to attach transformation functions to training datasets.
# 
# Hopsworks Feature Store also comes with built-in transformation functions such as `min_max_scaler`, `standard_scaler`, `robust_scaler` and `label_encoder`.

# In[10]:


[t_func.name for t_func in fs.get_transformation_functions()]


# We can retrieve transformation function we need .
# 
# To attach transformation function to training dataset provide transformation functions as dict, where key is feature name and value is online transformation function name.
# 
# Also training dataset must be created from the Query object. Once attached transformation function will be applied on whenever save, insert and get_serving_vector methods are called on training dataset object.

# In[11]:


# Load transformation functions.
standard_scaler = fs.get_transformation_function(name = 'standard_scaler')
label_encoder = fs.get_transformation_function(name = 'label_encoder')

#Map features to transformations.
mapping_transformers = {
    "rrp_positive": standard_scaler,
    "rrp_negative": standard_scaler,
    "school_day": label_encoder,
    "holiday": label_encoder
}


# ---
# 
# ## <span style="color:#ff5f27;">💼 Query Preparation</span>

# In[12]:


fg_weather.select_all().join(
                            fg_calendar.select_all()).show(5)


# In[13]:


fg_query = fg_weather.select_all()                        .join(
                            fg_calendar.select_all(),
                            on = ['index']
                        )\
                        .join(
                            fg_electricity.select_all(),
                            on = ['index']
                        )
fg_query.show(5)


# ---
# 
# ## <span style="color:#ff5f27;"> ⚙️ Feature View Creation </span>
# 
# `Feature Views` stands between **Feature Groups** and **Training Dataset**. Сombining **Feature Groups** we can create **Feature Views** which store a metadata of our data. Having **Feature Views** we can create **Training Dataset**.
# 
# The Feature Views allows schema in form of a query with filters, define a model target feature/label and additional transformation functions.
# 
# In order to create Feature View we can use `FeatureStore.create_feature_view()` method.
# 
# We can specify next parameters:
# 
# - `name` - name of a feature group.
# 
# - `version` - version of a feature group.
# 
# - `labels`- our target variable.
# 
# - `transformation_functions` - functions to transform our features.
# 
# - `query` - query object with data.

# In[14]:


feature_view = fs.create_feature_view(
    name = 'electricity_feature_view',
    version = 1,
    labels = ['demand'],
    query = fg_query
)


# In[15]:


feature_view


# For now `Feature View` is saved in Hopsworks and we can retrieve it using `FeatureStore.get_feature_view()`.

# In[16]:


feature_view = fs.get_feature_view(
    name = 'electricity_feature_view',
    version = 1
)


# In[17]:


feature_view.version


# ---
# 
# ## <span style="color:#ff5f27;"> 🏋️ Training Dataset Creation</span>
# 
# In Hopsworks training data is a query where the projection (set of features) is determined by the parent FeatureView with an optional snapshot on disk of the data returned by the query.
# 
# **Training Dataset  may contain splits such as:** 
# * Training set - the subset of training data used to train a model.
# * Validation set - the subset of training data used to evaluate hparams when training a model
# * Test set - the holdout subset of training data used to evaluate a mode
# 
# To create training dataset we use `FeatureView.create_training_data()` method.
# 
# Here are some importand things:
# 
# - It will inherit the name of FeatureView.
# 
# - The feature store currently supports the following data formats for
# training datasets: **tfrecord, csv, tsv, parquet, avro, orc**.
# 
# - We can choose necessary format using **data_format** parameter.
# 
# - **start_time** and **end_time** in order to filter dataset in specific time range.

# #### <span style="color:#ff5f27;"> ⛳️ Simple Training Dataset</span>

# In[18]:


feature_view.create_training_data(
    description = 'training_dataset',
    data_format = 'csv'
)


# - We can create **train, test** splits using `create_train_test_split()`. 
# 
# - We can create **train,validation, test** splits using `create_train_validation_test_splits()` methods.
# 
# - The only thing is that we should specify desired ratio of splits.

# #### <span style="color:#ff5f27;"> ⛳️ Dataset with train and test splits</span>

# In[19]:


feature_view.create_train_test_split(
    test_size = 0.2
)


# #### <span style="color:#ff5f27;"> ⛳️ Dataset with train, validation and test splits</span>

# In[20]:


feature_view.create_train_validation_test_split(
    validation_size = 0.2,
    test_size = 0.1
)


# ---
# 
# ## <span style="color:#ff5f27;"> 🪝 Retrieving Datasets </span>

# #### <span style="color:#ff5f27;"> ⛳️ Simple Training Dataset</span>

# In[21]:


X_train, y_train = feature_view.get_training_data(
    training_dataset_version = 1
)


# In[22]:


X_train.head()


# In[23]:


y_train.head()


# In[24]:


X_train.shape


# #### <span style="color:#ff5f27;"> ⛳️ Dataset with train and test splits</span>

# In[25]:


X_train, y_train, X_test, y_test = feature_view.get_train_test_split(
    training_dataset_version = 2
)


# In[26]:


X_train.head()


# In[27]:


X_train.shape


# In[28]:


X_test.shape


# #### <span style="color:#ff5f27;"> ⛳️ Dataset with train, validation and test splits</span>

# In[29]:


X_train, y_train, X_val, y_val, X_test, y_test = feature_view.get_train_validation_test_split(
    training_dataset_version = 3
)


# In[30]:


X_train.head()


# ---

# ## <span style="color:#ff5f27;"> 🔮 Creating Training Datasets with Event Time filter</span>
# 
# First of all lets import **datetime** from datetime library and set up a time format.
# 
# Then we can define start_time point and end_time point.
# 
# Finally we can create training dataset with data in specific time bourders. 
# 

# In[31]:


from datetime import datetime

def from_unix_to_datetime(unix):
    return datetime.utcfromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S')


# In[32]:


date_format = '%Y-%m-%d %H:%M:%S'

start_time_train = int(float(datetime.strptime('2017-01-01 00:00:01',date_format).timestamp()) * 1000)
end_time_train = int(float(datetime.strptime('2018-02-01 23:59:59',date_format).timestamp()) * 1000)

start_time_test = int(float(datetime.strptime('2018-02-02 23:59:59',date_format).timestamp()) * 1000)
end_time_test = int(float(datetime.strptime('2019-02-01 23:59:59',date_format).timestamp()) * 1000)


# #### <span style="color:#ff5f27;"> ⛳️ Simple Training Dataset with event time</span>

# In[33]:


feature_view.create_training_data(
    description = 'data_2017_2018',
    data_format = 'csv',
    start_time = start_time_train,
    end_time = end_time_train
)


# In[34]:


X_train_lim, y_train_lim = feature_view.get_training_data(
    training_dataset_version = 4
)


# #### <span style="color:#ff5f27;"> ⛳️ Training Dataset with train and test splits with event time</span>

# In[35]:


# feature_view.create_train_test_split(
#     test_size = 0.2,
#     train_start = start_time_train,
#     train_end = end_time_train,
#     test_start = start_time_test,
#     test_end = end_time_test
# )


# ---

# ### <span style="color:#ff5f27;"> Next Steps</span>
# 
# In the next notebook, we will train a model on the Training Dataset we created in this notebook.
