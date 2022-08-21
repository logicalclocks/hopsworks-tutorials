#!/usr/bin/env python
# coding: utf-8

# ![hopsworks_logo](../../images/hopsworks_logo.png)
#
# # Part 03: Model training & UI Exploration
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/logicalclocks/hopsworks-tutorials/blob/master/fraud_online/3_model_training.ipynb)
#
# In this last notebook, we will train a model on the dataset we created in the previous tutorial. We will train our model using standard Python and Scikit-learn, although it could just as well be trained with other machine learning frameworks such as PySpark, TensorFlow, and PyTorch. We will also show some of the exploration that can be done in Hopsworks, notably the search functions and the lineage.
#
# ## 🗒️ This notebook is divided in 5 main sections:
# 1. **Loading the training data**
# 2. **Train the model**
# 3. **Register model to Hopsworks model registry**.
# 4. **Deploy the model on KServe behind Hopsworks for real-time inference requests**.
# 5. **Test model deployment and use model serving rest APIs**.
#
# ![tutorial-flow](../../images/03_model.png)

# In[1]:


import hopsworks

project = hopsworks.login()

fs = project.get_feature_store()


# ---

# ## <span style="color:#ff5f27;"> ⬇️ Training Dataset retrieval</span>

# To retrieve training dataset from **Feature Store** we retrieve **Feature View** using `FeatureStore.get_feature_view` method.
#
# Then we can use **Feature View** in order to retrieve **training dataset** using `FeatureView.get_training_dataset` method.
#

# In[2]:


nyc_fares_fv = fs.get_feature_view(
    name = 'nyc_taxi_fares_fv',
    version = 1
)


# In[3]:


X_train, y_train, X_test, y_test = nyc_fares_fv.get_train_test_split(
    training_dataset_version=2
)


# In[4]:


X_test.head(5)


# In[5]:


cols_to_drop = ['ride_id']


# In[6]:


X_train = X_train.drop(cols_to_drop, axis=1)
X_test = X_test.drop(cols_to_drop, axis=1)


# In[7]:


import numpy as np


y_train = np.ravel(y_train)
y_test = np.ravel(y_test)


# In[8]:


y_test


# ---

# In[9]:


import pandas as pd

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import mean_absolute_error, r2_score


# ---

# In[10]:


X_test.shape


# ## <span style="color:#ff5f27;">🧬 Modeling</span>

# In[11]:


# we will not perform hyperparameter tuning cause the data was generated randomly
lr_model = LogisticRegression()

lr_model.fit(X_train, y_train)


# In[32]:


X_test.columns


# In[12]:


lr_preds = lr_model.predict(X_test)

lr_r2_score = r2_score(y_test, lr_preds)
lr_mae = mean_absolute_error(y_test, lr_preds)

print("LogisticRegression R²:", lr_r2_score)
print("LogisticRegression MAE:", lr_mae)


# ### Remember, our data is random, so the results are not accurate at all.

# ---

# ## <span style="color:#ff5f27;">📝 Register model in Hopsworks</span>
#
# One of the features in Hopsworks is the model registry. This is where we can store different versions of models and compare their performance. Models from the registry can then be served as API endpoints.
#
# Let's connect to the model registry using the [HSML library](https://docs.hopsworks.ai/machine-learning-api/latest) from Hopsworks.

# In[14]:


mr = project.get_model_registry()


# Before registering the model we will export it as a pickle file using joblib.

# In[15]:


import joblib

joblib.dump(lr_model, 'model.pkl')


# ### <span style="color:#ff5f27;">⚙️ Model Schema</span>

# The model needs to be set up with a [Model Schema](https://docs.hopsworks.ai/machine-learning-api/latest/generated/model_schema/), which describes the inputs and outputs for a model.
#
# A Model Schema can be automatically generated from training examples, as shown below.

# In[16]:


from hsml.schema import Schema
from hsml.model_schema import ModelSchema

input_schema = Schema(X_train)
output_schema = Schema(y_train)
model_schema = ModelSchema(input_schema=input_schema, output_schema=output_schema)

model_schema.to_dict()


# With the schema in place, we can finally register our model.

# In[17]:


metrics = {
    'mae': lr_mae,
    'r2_score': lr_r2_score
}


# In[18]:


model = mr.sklearn.create_model(
    name="nyc_taxi_fares_model",
    metrics=metrics,
    description="LogisticRegression.",
    input_example=X_test.sample(),
    model_schema=model_schema
)

model.save('model.pkl')


# In[19]:


# how to get a best model (when you have many of them)

# EVALUATION_METRIC="mae"  # or r2_score
# SORT_METRICS_BY="max" # your sorting criteria

# # get best model based on custom metrics
# best_model = mr.get_best_model("nyc_taxi_fares_model",
#                                EVALUATION_METRIC,
#                                SORT_METRICS_BY)


# Here we have also saved an input example from the training data, which can be helpful for test purposes.
#
# It's important to know that every time you save a model with the same name, a new version of the model will be saved, so nothing will be overwritten. In this way, you can compare several versions of the same model - or create a model with a new name, if you prefer that.

# ## <a class="anchor" id="1.5_bullet" style="color:#ff5f27"> 🚀 Model Deployment</a>

# In[20]:


# %%writefile predict_example.py
# import os
# import joblib
# import numpy as np
# import pandas as pd

# import hopsworks


# class Predict(object):

#     def __init__(self):
#         """ Initializes the serving state, reads a trained model"""
#         # get feature store handle
#         project = hopsworks.login()
#         self.fs = project.get_feature_store()

#         # load the trained model
#         self.model = joblib.load(os.environ["ARTIFACT_FILES_PATH"] + "/model.pkl")
#         print("Initialization Complete")

#     def predict(self, inputs):
#         """ Serves a prediction request usign a trained model"""
#         return self.model.predict(np.array(inputs).reshape(1, -1)).tolist()


# In[21]:


# import os

# # it may fail when you run it for the first time
# # just rerun this cell once again

# dataset_api = project.get_dataset_api()

# uploaded_file_path = dataset_api.upload("predict_example.py", "Models", overwrite=True)
# predictor_script_path = os.path.join("/Projects", project.name, uploaded_file_path)


# In[22]:


# On cluster, I have created this file manually cause it was not creating by itself

# predictor_script_path = f'hdfs:///Projects/{fs.project_name}/Jupyter/predict_example.py'


# In[23]:


# # check if it looks correct

# predictor_script_path


# In[24]:


# # since on my Windows it generated incorrectly, I will fix it manually.
# predictor_script_path = '/Projects/romankah/Models/predict_example.py'


# ---

# ## 📡 Create the deployment
# Here, we fetch the model we want from the model registry and define a configuration for the deployment. For the configuration, we need to specify the serving type (default or KFserving) and in this case, since we use default serving and an sklearn model, we need to give the location of the prediction script.

# In[ ]:


# # Give it any name you want
# deployment = model.deploy(
#     name="nyctaxifares",
#     model_server="PYTHON",
#     script_file=predictor_script_path,
#     serving_tool="KSERVE"
# )


# In[26]:


# print("Deployment: " + deployment.name)
# deployment.describe()


# ### The deployment has now been registered. However, to start it you need to run:

# In[27]:


# deployment.start()


# In[28]:


# deployment.get_logs()


# ## <span style='color:#ff5f27'>🔮 Predicting using deployment</span>

# In[29]:


# model.input_example


# In[30]:


# data = {
#     "inputs": model.input_example
# }

# deployment.predict(data)


# In[31]:


# deployment.stop()


# ---

# ## <span style="color:#ff5f27;"> 🎁  Wrapping things up </span>
#
# We have now performed a simple training with training data that we have created in the feature store. This concludes the fisrt module and introduction to the core aspect of the Feature store. In the second module we will introduce streaming and external feature groups for a similar fraud use case.
