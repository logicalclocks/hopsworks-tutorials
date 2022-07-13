import streamlit as st
import hopsworks
import plotly.graph_objs as go
import plotly.express as px

st.title('🔮 Churn Prediction Project')
st.text('Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()

st.write(fs)
st.text('Done ✅')
st.text('-------\n🪄 Retrieving Feature View...')

feature_view = fs.get_feature_view(
    name = 'churn_feature_view',
    version = 1
)

st.text('Done ✅')
st.text('-------\n⚙️ Reading DataFrame from Feature Groups...')

df_all = feature_view.query.read()

st.dataframe(df_all.head())
st.text(f'Shape: {df_all.shape}')
st.text('Done ✅')
st.text('-------\n👨🏻‍🎨 Building Plots...')

fig_gender = go.Figure()

fig_gender = px.histogram(
    df_all,
    x="gender",
    color="churn",
    title = 'Churn rate according to Gender'
)

fig_gender.update_xaxes(title = "Gender")
fig_gender.update_yaxes(title = "Count")
fig_gender.update_traces(hovertemplate = 'Gender: %{x} <br>Amount: %{y} <br>Churn: %{color}') 

fig_totalcharges = go.Figure()

fig_totalcharges = px.histogram(
    df_all,
    x="totalcharges",
    color="churn",
    title = 'Distribution of Total Charges according to Churn/Not'
)

fig_totalcharges.update_xaxes(title = "Charge Value")
fig_totalcharges.update_yaxes(title = "Count")
fig_totalcharges.update_traces(hovertemplate = 'Charge: %{x} <br>Count: %{y}') 

fig_paymentmethod = go.Figure()

fig_paymentmethod = px.histogram(
    df_all,
    x="paymentmethod",
    color="churn",
    title = 'Amount of each Payment Method'
)

fig_paymentmethod.update_xaxes(title = "Payment Method")
fig_paymentmethod.update_yaxes(title = "Total Amount")
fig_paymentmethod.update_traces(hovertemplate = 'Method: %{x} <br>Amount: %{y}') 

fig_partner = go.Figure()

fig_partner = px.histogram(
    df_all,
    x="partner",
    color="churn",
    title = 'Affect of having a partner on Churn/Not'
)

fig_partner.update_xaxes(title = "Have a partner")
fig_partner.update_yaxes(title = "Count")
fig_partner.update_traces(hovertemplate = 'Partner: %{x} <br>Amount: %{y}') 

st.plotly_chart(fig_gender)
st.plotly_chart(fig_totalcharges)
st.plotly_chart(fig_paymentmethod)
st.plotly_chart(fig_partner)
st.text('Done ✅')


st.text('-------\n🔮 Model Retrieving...')

mr = project.get_model_registry()
ms = project.get_model_serving()
model = mr.get_model("churnmodel", version = 1)
deployment = ms.get_deployment("churnmodel")

st.write(deployment)
st.text('Done ✅')
st.text('-------\n🚀 Model Start...')

deployment.start()

st.text('Done ✅')
st.text('-------\n📝 Input Example...')
st.write(model.input_example)

data = {
    "inputs": model.input_example
}

result = deployment.predict(data)

st.text(f'-------\n👩🏻‍⚖️ Prediction: {result}')
st.text('-------\n📝 Batch Data Prediction...')

batch_data = feature_view.get_batch_data()
st.dataframe(batch_data.head())

def get_predictions(row, deployment = deployment):
    data = {
        'inputs': row.tolist()
    }
    return deployment.predict(data)

result_batch = batch_data.iloc[:10].apply(get_predictions,axis = 1)

st.text(f'-------\n👩🏻‍⚖️ Predictions for 10 rows:\n {result_batch}')
st.text('-------\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
