import streamlit as st
import hopsworks
import plotly.graph_objs as go
import plotly.express as px
import joblib
import math
import pandas as pd

st.title('🔮 Customer Churn Prediction')

st.write(36 * "-")
st.header('\n📡 Connecting to Hopsworks Feature Store...')
project = hopsworks.login()
fs = project.get_feature_store()

st.write(fs)
st.text('Done ✅')
st.text('-------\n🪄 Retrieving Feature View...')

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def retrive_feature_view(fs = fs):
    feature_view = fs.get_feature_view(
        name = "churn_feature_view",
        version =  1
        )
    return feature_view

feature_view = retrive_feature_view()
st.text('Done ✅')
st.text('-------\n⚙️ Reading DataFrames from Feature View...')

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
st.text('Done ✅')
st.text('-------\n🔮 Model Retrieving...')

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_deployment(project = project):
    mr = project.get_model_registry()
    ms = project.get_model_serving()
    model = mr.get_model("churnmodel", version = 1)
    deployment = ms.get_deployment("churnmodel")
    deployment.start()
    return deployment,model

deployment, model = get_deployment()

st.write(deployment)
st.text('Done ✅')

st.text('-------\n📝 Input Example...')

def transform_preds(predictions):
    if type(predictions) == list:
        return ['Churn' if pred == 1 else 'Not Churn' for pred in predictions]
    return ['Churn' if pred == 1 else 'Not Churn' for pred in predictions['predictions']]

st.write(model.input_example)

data = {
    "inputs": model.input_example
}

result = deployment.predict(data)

st.text(f'👩🏻‍⚖️ Prediction: {transform_preds(result)}')
st.text('-------\n📝 Batch Data Prediction...')

st.dataframe(batch_data.head())

def get_predictions(row, deployment = deployment):
    data = {
        'inputs': row.tolist()
    }
    return deployment.predict(data)

predictions = [pred['predictions'][0] for pred in batch_data[:500].apply(get_predictions,axis = 1)]
predictions = transform_preds(predictions)

df_all['Churn'] = predictions

result_table = df_all[['customerid','Churn']]

st.text(f'👩🏻‍⚖️ Predictions for 5 rows:\n {predictions[:5]}')
st.text('-------\n💳 Prediction by Customer Id...')

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

st.text('-------\n👨🏻‍🎨 Prediction Visualizing...')

model_lr = joblib.load('churnmodel.pkl')
importance = model_lr.coef_[0]

feature_names = batch_data.columns

feature_importance = pd.DataFrame(feature_names, columns = ["feature"])
feature_importance["importance"] = pow(math.e, model_lr.coef_[0])
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

st.text('Done ✅')
st.text('-------\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
