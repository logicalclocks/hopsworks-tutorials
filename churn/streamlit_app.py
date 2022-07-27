import streamlit as st
import hopsworks
import hsfs
import plotly.graph_objs as go
import plotly.express as px
import joblib
import math
import pandas as pd

st.title('🔮 Customer Churn Prediction')

st.write(36 * "-")
st.header('\n📡 Connecting to Hopsworks Feature Store...')

def header(text):
    st.write(36 * "-")
    st.write('#### ' + text)

conn = hsfs.connection(
    host="0f060790-06a4-11ed-8aed-d1422d4ec537.cloud.hopsworks.ai",                               
    project="churn",                    
    hostname_verification=False,                     
    api_key_value="API_KEY"         
)
fs = conn.get_feature_store()     

hopsworks_conn = hopsworks.connection(
    host="0f060790-06a4-11ed-8aed-d1422d4ec537.cloud.hopsworks.ai",                              
    project="churn",                     
    hostname_verification=False,                     
    api_key_value="API_KEY"        
)

project = hopsworks_conn.get_project()

st.write(fs)
header('🪄 Retrieving Feature View...')

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def retrive_feature_view(fs = fs):
    feature_view = fs.get_feature_view(
        name = "churn_feature_view",
        version =  1
        )
    return feature_view

feature_view = retrive_feature_view()
st.text('Done ✅')
header('⚙️ Reading DataFrames from Feature View...')

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def retrive_data(feature_view = feature_view):
    batch_data = feature_view.get_batch_data()
    batch_data.drop('customerid',axis = 1, inplace = True)
    df_all = feature_view.query.read()[:500]
    df_all.drop('churn',axis = 1, inplace = True)
    return batch_data,df_all

batch_data, df_all = retrive_data()

st.dataframe(df_all.head())
st.text(f'Shape: {df_all.shape}')
header('🔮 Model Retrieving...')

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_model(project = project):
    mr = project.get_model_registry()
    model = mr.get_model("churnmodel", version = 1)
    model_dir = model.download()
    return joblib.load(model_dir + "/churnmodel.pkl")

model = get_model()

st.write(model)

def transform_preds(predictions):
    return ['Churn' if pred == 1 else 'Not Churn' for pred in predictions]

header('📝 Batch Data Prediction...')

st.dataframe(batch_data.head())


predictions = model.predict(batch_data[:500])
predictions = transform_preds(predictions)

df_all['Churn'] = predictions

result_table = df_all[['customerid','Churn']]

st.text(f'👩🏻‍⚖️ Predictions for 5 rows:\n {predictions[:5]}')
header('💳 Prediction by Customer Id...')

with st.form(key="Selecting Customer ID"):
    option = st.selectbox(
             'Select a Custimer ID to return a predict.',
             (result_table.customerid.values[:15])
          )
    submit_button = st.form_submit_button(label='Submit')

if submit_button:   
    result = result_table[result_table.customerid == option]['Churn'].values

    st.text(f'👮🏻‍♂️ Customer ID: {option}')
    st.text(f'👩🏻‍⚖️ Prediction: {result}')

header('👨🏻‍🎨 Prediction Visualizing...')


feature_names = batch_data.columns

feature_importance = pd.DataFrame(feature_names, columns = ["feature"])
feature_importance["importance"] = pow(math.e, model.coef_[0])
feature_importance = feature_importance.sort_values(by = ["importance"], ascending = False)

fig_importance = px.bar(
    feature_importance,
    x='feature',
    y='importance',
    title = 'Feature Importance Plot'
     )

fig_importance.update_xaxes(tickangle = 23)
fig_importance.update_xaxes(title = "Feature")
fig_importance.update_yaxes(title = "Importance")
fig_importance.update_traces(hovertemplate = 'Feature: %{x} <br>Importance: %{y}') 

st.plotly_chart(fig_importance)

def plot_histogram(data, x_col, title, xlabel, ylabel):

    fig = go.Figure()

    fig = px.histogram(
        data,
        x = x_col,
        color="Churn",
        title = title
    )

    fig.update_xaxes(title = xlabel)
    fig.update_yaxes(title = ylabel)
    fig.update_traces(hovertemplate = xlabel + ': %{x} <br>' + ylabel + ': %{y}')

    return fig

st.plotly_chart(plot_histogram(df_all, 'gender','Churn rate according to Gender','Gender', 'Count'))
st.plotly_chart(plot_histogram(df_all,'totalcharges','Distribution of Total Charges according to Churn/Not',"Charge Value",'Count'))
st.plotly_chart(plot_histogram(df_all,'paymentmethod','Amount of each Payment Method',"Payment Method",'Total Amount'))
st.plotly_chart(plot_histogram(df_all,'partner','Affect of having a partner on Churn/Not',"Have a partner",'Count'))

st.success('🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')    
st.balloons()
