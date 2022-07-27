import streamlit as st
import hsfs
import hopsworks
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
import joblib

import warnings
warnings.filterwarnings('ignore')


st.title('🔮 📈 Electricity Demand Prediction')
st.write(36 * "-")
st.subheader("📡 Connecting to Hopsworks Feature Store...")

conn = hsfs.connection(
    host="0f060790-06a4-11ed-8aed-d1422d4ec537.cloud.hopsworks.ai",                               
    project="electricity_demand",                      
    hostname_verification=False,                    
    api_key_value="API_KEY"         
)
fs = conn.get_feature_store()     

hopsworks_conn = hopsworks.connection(
    host="0f060790-06a4-11ed-8aed-d1422d4ec537.cloud.hopsworks.ai",                              
    project="electricity_demand",                     
    hostname_verification=False,                     
    api_key_value="API_KEY"        
)

project = hopsworks_conn.get_project()

st.write(fs)

def header(text):
    st.write(36 * "-")
    st.write('#### ' + text)
    

header('🪄 Retrieving Feature View...')


def to_date(unix):
    return datetime.utcfromtimestamp(unix / 1000).strftime('%Y-%m-%d %H:%M:%S')

@st.cache(suppress_st_warning=True)
def retrieving_data(fs = fs):
    feature_view = fs.get_feature_view(
        name = 'electricity_feature_view',
        version = 1
    )
    data = feature_view.query.read()
    data.sort_values('date', inplace = True)
    data.date = pd.to_datetime(data.date.apply(to_date))

    return feature_view, data

feature_view, data = retrieving_data()

st.write(data.head())
header('👨🏻‍🎨 Data Visualisation...')

def plot_trend(data, y_col, title, xlabel, ylabel,log_scale = False):
    
    fig = px.line(
        data,
        x = 'date',
        y = y_col,
        title = title,
        log_y = log_scale
    )

    fig.update_xaxes(title = xlabel)
    fig.update_yaxes(title = ylabel)
    fig.update_traces(hovertemplate = xlabel + ': %{x} <br>' + ylabel + ': %{y}')

    return fig

fig_demand = plot_trend(data,'demand','Daily electricity demand from January 2015 to October 2020','Date','Demand MWh')
fig_price = plot_trend(data,'rrp','Daily price in AUD$/MWh from January 2015 to October 2020','Date','Price in AUD$/MWh',True)
fit_temperature = plot_trend(data,['min_temperature','max_temperature'],'Daily min and max temperature from January 2015 to October 2020','Date','Temperature in Celsius')

st.plotly_chart(fig_demand)
st.plotly_chart(fig_price)
st.plotly_chart(fit_temperature)


header('🚀 Model Retrieving...')

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_model(project = project):
    mr = project.get_model_registry()
    model = mr.get_model("forestmodel", version = 1)
    model_dir = model.download()
    return joblib.load(model_dir + "/forest.pkl")


model = get_model()

st.write(model)
header('🔮 Batch Prediction...')

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def retrieving_batch_data(feature_view = feature_view):
    batch = feature_view.get_batch_data().drop('index', axis = 1)
    return batch.sort_values('date')
     

batch = retrieving_batch_data()
batch['predictions'] = model.predict(batch.drop('date', axis = 1))
batch.date = pd.to_datetime(batch.date.apply(to_date))

fig_preds = plot_trend(batch,'predictions','Electricity demand prediction from January 2015 to October 2020','Date','Demand MWh')

st.plotly_chart(fig_preds)

st.write(36 * "-")
st.success('🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')    
st.balloons()


