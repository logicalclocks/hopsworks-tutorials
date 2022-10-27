import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium, folium_static
import json
import time
from datetime import timedelta, datetime
from branca.element import Figure

from functions import decode_features, get_model


def fancy_header(text, font_size=24):
    res = f'<span style="color:#ff5f27; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )


st.title('⛅️Air Quality Prediction Project🌩')

progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.write(36 * "-")
fancy_header('\n📡 Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()
feature_view = fs.get_feature_view(
    name = 'air_quality_fv',
    version = 1
)

st.write("Successfully connected!✔️")
progress_bar.progress(20)

st.write(36 * "-")
fancy_header('\n☁️ Getting batch data from Feature Store...')

start_date = datetime.now() - timedelta(days=1)
start_time = int(start_date.timestamp()) * 1000

X = feature_view.get_batch_data(start_time=start_time)
progress_bar.progress(50)

latest_date_unix = str(X.date.values[0])[:10]
latest_date = time.ctime(int(latest_date_unix))

st.write(f"⏱ Data for {latest_date}")

X = X.drop(columns=["date"]).fillna(0)

data_to_display = decode_features(X, feature_view=feature_view)

progress_bar.progress(60)

st.write(36 * "-")
fancy_header(f"🗺 Processing the map...")

fig = Figure(width=550,height=350)

my_map = folium.Map(location=[58, 20], zoom_start=3.71)
fig.add_child(my_map)
folium.TileLayer('Stamen Terrain').add_to(my_map)
folium.TileLayer('Stamen Toner').add_to(my_map)
folium.TileLayer('Stamen Water Color').add_to(my_map)
folium.TileLayer('cartodbpositron').add_to(my_map)
folium.TileLayer('cartodbdark_matter').add_to(my_map)
folium.LayerControl().add_to(my_map)

data_to_display = data_to_display[["city", "temp", "humidity",
                                            "conditions", "aqi"]]

cities_coords = {("Sundsvall", "Sweden"): [62.390811, 17.306927],
                 ("Stockholm", "Sweden"): [59.334591, 18.063240],
                 ("Malmo", "Sweden"): [55.604981, 13.003822]}

if "Kyiv" in data_to_display["city"]:
    cities_coords[("Kyiv", "Ukraine")]: [50.450001, 30.523333]

data_to_display = data_to_display.set_index("city")

cols_names_dict = {"temp": "Temperature",
                   "humidity": "Humidity",
                   "conditions": "Conditions",
                   "aqi": "AQI"}

data_to_display = data_to_display.rename(columns=cols_names_dict)

cols_ = ["Temperature", "Humidity", "AQI"]
data_to_display[cols_] = data_to_display[cols_].apply(lambda x: round(x, 1))

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

    folium.Marker(
        cities_coords[(city, country)], popup=text, tooltip=f"<strong>{city}</strong>"
    ).add_to(my_map)


# call to render Folium map in Streamlit
folium_static(my_map)
progress_bar.progress(80)
st.sidebar.write("-" * 36)


model = get_model(project=project,
                  model_name="gradient_boost_model",
                  evaluation_metric="f1_score",
                  sort_metrics_by="max")

preds = model.predict(X)

cities = [city_tuple[0] for city_tuple in cities_coords.keys()]

next_day_date = datetime.today() + timedelta(days=1)
next_day = next_day_date.strftime ('%d/%m/%Y')
df = pd.DataFrame(data=preds, index=cities, columns=[f"AQI Predictions for {next_day}"], dtype=int)

st.sidebar.write(df)
progress_bar.progress(100)
st.button("Re-run")
