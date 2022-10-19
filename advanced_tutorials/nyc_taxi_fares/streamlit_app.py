import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json
import time

from functions import *

def print_fancy_header(text, font_size=24):
    res = f'<span style="color:#ff5f27; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )


progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.title('🚖NYC Taxi Fares Project🚖')
st.write(36 * "-")
print_fancy_header('\n📡 Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()

rides_fg = fs.get_or_create_feature_group(name="nyc_taxi_rides",
                                          version=1)

fares_fg = fs.get_or_create_feature_group(name="nyc_taxi_fares",
                                          version=1)

progress_bar.progress(20)
st.write("Successfully connected!✔️")

def get_random_map_points(n):
    res = list()
    for i in range(n):
        res.append([round(np.random.uniform(40.5, 41.8), 5),
                    round(np.random.uniform(-74.5, -72.8), 5)])
    return res


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
            EVALUATION_METRIC="mae"  # or r2_score
            SORT_METRICS_BY="max"
            # get best model based on custom metrics
            model = mr.get_best_model("nyc_taxi_fares_model",
                                      EVALUATION_METRIC,
                                      SORT_METRICS_BY)
            model_dir = model.download()
            model = joblib.load(model_dir + "/model.pkl")

    progress_bar.progress(80)

    return model


def process_input_vector(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude):
    df = pd.DataFrame.from_dict({
        "ride_id": [secrets.token_hex(nbytes=16)],
        "pickup_datetime": [np.random.randint(1600000000, 1610000000)],
        "pickup_longitude": [pickup_longitude],
        "dropoff_longitude": [dropoff_longitude],
        "pickup_latitude": [pickup_latitude],
        "dropoff_latitude": [dropoff_latitude],
        "passenger_count": [np.random.randint(1, 5)],
        "tolls": [np.random.randint(0, 6)],
        "taxi_id": [np.random.randint(1, 201)],
        "driver_id": [np.random.randint(1, 201)]
    })

    df = calculate_distance_features(df)
    df = calculate_datetime_features(df)

    for col in ["passenger_count", "taxi_id", "driver_id"]:
        df[col] = df[col].astype("int64")

    return df


st.write(36 * "-")
print_fancy_header('\n🧩 Enter the the pick-up and dropoff coordinates...')
st.write("🔺 Click on the map and wait couple of seconds:")
# st.write("**🌇 NYC coordinates: Latitude - (40.5, 41.8), Longitude - (-74.5, -72.8)**")

my_map = folium.Map(location=[41, -73.5], zoom_start=8)

my_map.add_child(folium.LatLngPopup())
folium.TileLayer('Stamen Terrain').add_to(my_map)
folium.TileLayer('Stamen Toner').add_to(my_map)
folium.TileLayer('Stamen Water Color').add_to(my_map)
folium.TileLayer('cartodbpositron').add_to(my_map)
folium.TileLayer('cartodbdark_matter').add_to(my_map)
folium.LayerControl().add_to(my_map)

coordinates = json.load(open("temp_coordinates.json"))


res_map = st_folium(my_map, height=300, width=600)


progress_bar.progress(30)

try:
    new_lat, new_long = res_map["last_clicked"]["lat"], res_map["last_clicked"]["lng"]

    # lets rewrite lat and long for the older coordinate
    if coordinates["c1"]["time_clicked"] > coordinates["c2"]["time_clicked"]:
        target = "c2"

    else:
        target = "c1"

    coordinates[target] = {
        "lat": new_lat,
        "long": new_long,
        "time_clicked": time.time()
    }

    pickup_latitude, pickup_longitude = coordinates["c1"]["lat"], coordinates["c1"]["long"]
    dropoff_latitude, dropoff_longitude = coordinates["c2"]["lat"], coordinates["c2"]["long"]

    # display selected points
    col1, col2 = st.columns(2)
    with col1:
        st.write("🟡 Pick-up coordinates:")
        st.write(f"Latitude: {pickup_latitude}")
        st.write(f"Longitude: {pickup_longitude}")
    with col2:
        st.write("🔵 Destination coordinates:")
        st.write(f"Latitude: {dropoff_latitude}")
        st.write(f"Longitude: {dropoff_longitude}")


    json.dump(coordinates, open("temp_coordinates.json", "w" ))


###############################################################
# sliders instead of map
# pickup_latitude = st.slider(
#      'Pick-up Latitude',
#      40.5, 41.8)
# pickup_longitude = st.slider(
#      'ick-up Longitude',
#      -74.5, -72.8)
#
# print_fancy_header("🔻 Please enter the coordinates of the destination:")
# dropoff_latitude = st.slider(
#      'Destination Latitude',
#      40.5, 41.8)
# dropoff_longitude = st.slider(
#      'Destination Longitude',
#      -74.5, -72.8)
################################################################

    passenger_count = st.selectbox(
         '👥 Please enter the number of passengers:',
         (1, 2, 3, 4))

    progress_bar.progress(45)

    st.write(36 * "-")
    print_fancy_header('\n🤖 Feature Engineering...')
    df = process_input_vector(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)

    # X features
    X = df.drop(columns=['ride_id', 'taxi_id', 'driver_id', 'pickup_latitude', 'pickup_longitude',
                         'dropoff_latitude', 'dropoff_longitude', 'pickup_datetime'])

    st.dataframe(X)
    progress_bar.progress(60)

    st.write(36 * "-")
    print_fancy_header('\n🧠 Making price prediction for your trip...')
    model = get_model()
    progress_bar.progress(75)
    prediction = model.predict(X)[0]

    st.subheader(f"Prediction: **{str(prediction)}**")

    progress_bar.progress(85)

    st.write(36 * "-")

    if st.button('📡 Insert this new data to Hopsworks Feature Store'):
        st.write("⬆️ Inserting a new data to the 'rides' Feature Group...")
        print("Inserting into RIDES FG.")
        rides_cols = ['ride_id', 'pickup_datetime', 'pickup_longitude', 'dropoff_longitude',
                      'pickup_latitude', 'dropoff_latitude', 'passenger_count', 'taxi_id',
                      'driver_id', 'distance', 'pickup_distance_to_jfk',
                      'dropoff_distance_to_jfk', 'pickup_distance_to_ewr',
                      'dropoff_distance_to_ewr', 'pickup_distance_to_lgr',
                      'dropoff_distance_to_lgr', 'year', 'weekday', 'hour']

        rides_fg.insert(df[rides_cols])
        progress_bar.progress(93)

        st.write("⬆️ Inserting a new data to the 'fares' Feature Group...")
        print("Inserting into FARES FG.")
        fares_cols = ['tolls', 'taxi_id', 'driver_id', 'ride_id']

        df_fares = df[fares_cols]
        df_fares["total_fare"] = prediction
        for col in ["tolls", "total_fare"]:
            df_fares[col] = df_fares[col].astype("double")

        fares_fg.insert(df_fares)

        print_fancy_header('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')

    progress_bar.progress(100)

except Exception as err:
    print(err)
    pass

st.button("Re-run")
