import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium, folium_static
import json
import time
import datetime
from branca.element import Figure


def get_model():
    # load our Model
    import os
    TARGET_FILE = "model.pkl"
    list_of_files = [os.path.join(dirpath,filename) for dirpath, _, filenames in os.walk('.') for filename in filenames if filename == TARGET_FILE]

    if list_of_files:
        model_path = list_of_files[0]
        model = joblib.load(model_path)
    else:
        if not os.path.exists(TARGET_FILE):
            mr = project.get_model_registry()
            EVALUATION_METRIC="f1_score"
            SORT_METRICS_BY="max"
            # get best model based on custom metrics
            model = mr.get_best_model("gradient_boost_model",
                                       EVALUATION_METRIC,
                                       SORT_METRICS_BY)
            model_dir = model.download()
            model = joblib.load(model_dir + "/model.pkl")


    return model


st.title('⛅️Air Quality Prediction Project🌩')


progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.write(36 * "-")
st.subheader('\n📡 Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()

st.write("Successfully connected!✔️")
progress_bar.progress(20)

st.write(36 * "-")
st.subheader('\n☁️ Getting data from Feature Store...')


@st.cache(suppress_st_warning=True)
def get_recent_data():
    feature_view = fs.get_feature_view(name="air_quality_fv")
    data_to_display = feature_view.query.read().sort_values(by=["date", 'city'],
                                                ascending=[False, True]).head(4)
    X = feature_view.get_training_data(1)[0].sort_values(by=["date", "city"],
                                                         ascending=[False, True]).head(4)
    X = X.drop(columns=["date"])
    return data_to_display, X


data_to_display, X = get_recent_data()
progress_bar.progress(50)

latest_date_unix = str(data_to_display.date.values[0])[:10]

import time
latest_date = time.ctime(int(latest_date_unix))

st.write(f"⏱ Data for {latest_date}")

progress_bar.progress(60)

# train_data = feature_view.get_training_data(1)[0]
# train_data.sort_values(by=["date", 'city']).head(4)


# st.sidebar.write(recent_data[["city", "aqi"]])
st.write(36 * "-")
st.subheader(f"🗺 Processing the map...")

data_to_display = data_to_display[["city", "temp", "humidity",
                                            "conditions", "aqi"]]
data_to_display = data_to_display.set_index("city")

cols_names_dict = {"temp": "Temperature",
                   "humidity": "Humidity",
                   "conditions": "Conditions",
                   "aqi": "AQI"}

data_to_display = data_to_display.rename(columns=cols_names_dict)
progress_bar.progress(75)
#
#     st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')


fig = Figure(width=550,height=350)

my_map = folium.Map(location=[56, 20], zoom_start=3.71)
fig.add_child(my_map)
folium.TileLayer('Stamen Terrain').add_to(my_map)
folium.TileLayer('Stamen Toner').add_to(my_map)
folium.TileLayer('Stamen Water Color').add_to(my_map)
folium.TileLayer('cartodbpositron').add_to(my_map)
folium.TileLayer('cartodbdark_matter').add_to(my_map)
folium.LayerControl().add_to(my_map)


cities_coords = {("Kyiv", "Ukraine"): [50.450001, 30.523333],
               ("Sundsvall", "Sweden"): [62.390811, 17.306927],
               ("Stockholm", "Sweden"): [59.334591, 18.063240],
               ("Malmo", "Sweden"): [55.604981, 13.003822]}



for city, country in cities_coords:
    text = f"""
            <h4 style="color:green;">{city}</h4>
            <h5 style="color":"green">
                <table style="text-align: right;">
                    <tr>
                        <th>Country:</th>
                        <td><b>{country}</b></td>
                    </tr>
                    """
    for column in data_to_display.columns:
        text += f"""
                    <tr>
                        <th>{column}:</th>
                        <td>{data_to_display.loc[city][column]}</td>
                    </tr>"""
    text += """</table>
                    </h5>"""

    # text = f'<h3 style="color:green;">{city}</h3><h4>Air quality: 12;<br>Temperature: 24</h4>'
    folium.Marker(
        cities_coords[(city, country)], popup=text, tooltip=f"<strong>{city}</strong>"
    ).add_to(my_map)


# call to render Folium map in Streamlit
folium_static(my_map)

progress_bar.progress(80)
st.sidebar.write("-" * 36)


model = get_model()
preds = model.predict(X)

cities = ["Malmo", "Stockholm", "Sundsvall", "Kyiv"]


next_day_date = datetime.datetime.today() + datetime.timedelta(days=1)
next_day = next_day_date.strftime ('%d/%m/%Y')
df = pd.DataFrame(data=preds, index=cities, columns=[f"AQI Predictions for {next_day}"], dtype=int)
st.sidebar.write(df)

progress_bar.progress(100)

# st.sidebar.markdown(text)
st.button("Re-run")
