import streamlit as st
import hopsworks
from hsfs.feature import Feature
from features.price import plot_historical_id, plot_prediction
import joblib
from datetime import datetime, timedelta

st.header('📈 🔮Batch Inference Pipeline')

@st.cache_resource()
def get_feature_store():
    st.markdown('📡 Connecting to Hopsworks Feature Store...')

    project = hopsworks.login()
    fs = project.get_feature_store()

    st.write("✅ Logged in successfully!")

    return project, fs

@st.cache_resource()
def get_feature_group():
    st.write("🪝 Retrieving the Price Feature Group...")
    price_fg = fs.get_feature_group(
        name='price',
        version=1,
    )
    st.write("✅ Success!")

    return price_fg

@st.cache_resource()
def get_feature_view():
    st.write("🪝 Retrieving the Feature View...")
    feature_view = fs.get_feature_view(
        name = 'price_fv3',
        version = 1
    )
    st.write("✅ Success!")

    return feature_view

project, fs = get_feature_store()
price_fg = get_feature_group()
feature_view = get_feature_view()


@st.cache_data()
def get_data_from_feature_group(_price_fg):
    st.write("🪝 Retrieving Data from Feature Store...")
    data = price_fg.read()

    st.write("✅ Success!")

    return data

data = get_data_from_feature_group(price_fg)

fig = plot_historical_id([1, 2], data)

st.plotly_chart(fig)


@st.cache_resource()
def retrieve_model():
    st.write("⚙️ Retrieving Model from Model Registry...")
    mr = project.get_model_registry()
    retrieved_model = mr.get_model(
        name="xgboost_price_model2",
        version=1,
    )
    saved_model_dir = retrieved_model.download()
    model = joblib.load(saved_model_dir + "/xgboost_price_model2.pkl")

    st.write("✅ Success!")

    return model

model = retrieve_model()


@st.cache_data()
def get_batch_last_week():
    st.write("⚙️ Retrieving Batch Data for the last week...")
    # Get today's date
    today = datetime.today()

    # Calculate the date 7 days ago
    week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    # Initialise feature view to retrieve batch data
    feature_view.init_batch_scoring(training_dataset_version=1)

    # Retrieve batch data
    batch_data = feature_view.get_batch_data(
        start_time=week_ago,
        end_time=today.strftime("%Y-%m-%d"),
    )
    
    st.write("✅ Success!")

    return batch_data, week_ago

batch_data, week_ago = get_batch_last_week()

def predict_id(id_value, data, model):
    data_filtered = data[data.id == id_value]
    preds = model.predict(data_filtered)
    return preds

id = 1
predictions = predict_id(id, batch_data.drop('date', axis=1), model)

fig_pred = plot_prediction(id, data, week_ago, predictions)

st.plotly_chart(fig_pred)

st.write(36 * "-")
st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')