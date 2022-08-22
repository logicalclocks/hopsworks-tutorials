#!/usr/bin/env python
# coding: utf-8

# # <span style="font-width:bold; font-size: 3rem; color:#1EB182;"><img src="images/icon102.png" width="38px"></img> **Hopsworks Feature Store** </span><span style="font-width:bold; font-size: 3rem; color:#333;">- Part 03: Model training</span>
# 
# <span style="font-width:bold; font-size: 1.4rem;">In this last notebook, we will train a model on the dataset we created in the previous tutorial. We can train our model using standard Python and machine learning frameworks such as Scikit-learn, PySpark, TensorFlow, and PyTorch.</span>
# 
# ## 🗒️ This notebook is divided in 3 main sections:
# 1. Loading the training data.
# 2. Model training.
# 3. Model's Predictions Visualization.
# 
# ![tutorial-flow](images/03_model.png)

# ---
# ## <span style="color:#ff5f27;"> 🔮 Connecting to Hopsworks Feature Store </span>

# In[1]:


import hopsworks

project = hopsworks.login()

fs = project.get_feature_store() 


# ---
# 
# ## <span style="color:#ff5f27;">🪝 Feature View and Training Dataset Retrieval</span>

# To retrieve training dataset from Feature Store we retrieve **Feature View** using `FeatureStore.get_feature_view()` method.
# 
# Then we can use **Feature View** in order to retrieve **training dataset** using `FeatureView.get_train_test_split()` method.

# In[2]:


feature_view = fs.get_feature_view(
    name = 'electricity_feature_view',
    version = 1
)


# In[3]:


X_train, y_train, X_test, y_test = feature_view.get_train_test_split(
    training_dataset_version = 2
)


# In[4]:


X_train.head()


# ---
# 
# ## <span style="color:#ff5f27;">🤖 Model Building</span>

# ### <span style="color:#ff5f27;">📝 Imports</span>

# In[5]:


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score


# ### <span style="color:#ff5f27;">🧑🏻‍🔬 RandomForestRegressor</span>

# In[6]:


reg = RandomForestRegressor(
    n_estimators = 25,
    max_features = 'sqrt',
    n_jobs = -1,
    random_state = 42
)

reg.fit(X_train.drop(['index','date'], axis = 1),y_train)


# In[7]:


preds = reg.predict(X_test.drop(['index','date'],axis = 1))

r2_score(y_test, preds)


# ---
# 
# ## <span style="color:#ff5f27;">🔬 🧬 Model Predictions Visualization</span>

# In[8]:


X_test['preds'] = preds
X_train['target'] = y_train
X_train.date = pd.to_datetime(X_train.date)
X_test.date = pd.to_datetime(X_test.date)


# In[9]:


fig,ax = plt.subplots(figsize = (16,5))

X_train.plot('date','target', ax = ax)
X_test.plot('date','preds', ax = ax)

ax.set_xlabel('Date',fontsize = 15)
ax.set_ylabel('Demand',fontsize = 15)
ax.set_title('Real Demand VS Predicted Demand from January 2015 to October 2020',fontsize = 20)

plt.show()


# ---
# ## <span style='color:#ff5f27'>👮🏼‍♀️ Model Registry</span>

# In[10]:


#import hsml

#conn = hsml.connection()
#mr = conn.get_model_registry()


# In[11]:


#from hsml.schema import Schema
#from hsml.model_schema import ModelSchema

#input_schema = Schema(X_train.drop(['index','date','target'],axis = 1))
#output_schema = Schema(y_train)
#model_schema = ModelSchema(input_schema=input_schema, output_schema=output_schema)

#model_schema.to_dict()


# In[12]:


import joblib

pkl_file_name = "forest.pkl"

joblib.dump(reg, pkl_file_name)

model = mr.sklearn.create_model(
    name = "forestmodel",
    input_example = X_train.drop(['index','date','target'],axis = 1).sample(),
    model_schema = model_schema
)

model.save(pkl_file_name)


# ---
# 
# ## <span style='color:#ff5f27'>🚀 Model Deployment</span>

# In[13]:


#get_ipython().run_cell_magic('writefile', 'predict_example.py', 'import os\nimport joblib\nimport numpy as np\nimport pandas as pd\n\nclass Predict(object):\n\n    def __init__(self):\n        """ Initializes the serving state, reads a trained model"""        \n        # load the trained model\n        self.model = joblib.load(os.environ["ARTIFACT_FILES_PATH"] + "/forest.pkl")\n        print("Initialization Complete")\n\n    def predict(self, inputs):\n        """ Serves a prediction request usign a trained model"""\n        return self.model.predict(np.array(inputs).reshape(1, -1)).tolist()')


# In[14]:


#import os
#dataset_api = project.get_dataset_api()

#uploaded_file_path = dataset_api.upload("predict_example.py", "Models", overwrite=True)
#predictor_script_path = os.path.join("/Projects", project.name, uploaded_file_path)


# In[15]:


# Use the model name from the previous notebook.
model = mr.get_model("forestmodel", version = 1)

# Give it any name you want
#deployment = model.deploy(
#    name="forestmodeldeploy", 
#    model_server="PYTHON",
#    serving_tool='KSERVE',
#    script_file=predictor_script_path
#)


# In[16]:


# get Hopsworks Model Serving
#ms = project.get_model_serving()

# get deployment object
#deployment = ms.get_deployment("forestmodeldeploy")


# In[17]:


#deployment.start(await_running = 120)


# In[18]:


#deployment.get_logs()


# ---
# ## <span style='color:#ff5f27'>🔮 Predicting</span>

# In[19]:


batch = feature_view.get_batch_data()
batch.sort_values('date',inplace = True)
batch.drop(['index','date'], axis = 1, inplace = True)
batch.head()


# In[20]:


batch.shape


# In[21]:


#def get_predictions(row, deployment = deployment):
#    data = {
#        'inputs': row.tolist()
#    }
#    return deployment.predict(data)


# In[22]:


#predictions = [pred['predictions'][0] for pred in batch[:500].apply(get_predictions,axis = 1)]

#predictions[:5]


# ---
