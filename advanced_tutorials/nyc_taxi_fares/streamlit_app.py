import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json
import time
import secrets

from features import nyc_taxi_rides


def print_fancy_header(text, font_size=22, color="#ff5f27"):
    res = f'<span style="color:{color}; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )

def get_model(project, model_name, file_name):
    # load our Model
    import os
    TARGET_FILE = f"{file_name}.pkl"
    list_of_files = [os.path.join(dirpath,filename) for dirpath, _, filenames in os.walk('.') for filename in filenames if filename == TARGET_FILE]

    if list_of_files:
        model_path = list_of_files[0]
        model = joblib.load(model_path)
    else:
        if not os.path.exists(TARGET_FILE):
            mr = project.get_model_registry()
            EVALUATION_METRIC="mae"
            SORT_METRICS_BY="max"
            # get best model based on custom metrics
            model = mr.get_best_model(model_name,
                                      EVALUATION_METRIC,
                                      SORT_METRICS_BY)
            model_dir = model.download()
            model = joblib.load(model_dir + f"/{file_name}.pkl")

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

    df = nyc_taxi_rides.calculate_distance_features(df)
    df = nyc_taxi_rides.calculate_datetime_features(df)

    for col in ["passenger_count", "taxi_id", "driver_id"]:
        df[col] = df[col].astype("int64")

    return df



st.title('🚖NYC Taxi Fares Project🚖')
st.write(36 * "-")
print_fancy_header('\n📡 Connecting to the Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()

rides_fg = fs.get_or_create_feature_group(name="nyc_taxi_rides",
                                          version=1)

fares_fg = fs.get_or_create_feature_group(name="nyc_taxi_fares",
                                          version=1)
st.write("Successfully connected!✔️")


with st.form(key="user_inputs"):
    print_fancy_header(text="👥 Please enter the number of passengers:",
                       font_size=24, color="#00FFFF")
    passenger_count = st.selectbox(label='',
                                   options=(1, 2, 3, 4))

    st.write(36 * "-")

    print_fancy_header(text='\n🚕 Enter the the pick-up and dropoff coordinates using map',
                       font_size=24, color="#00FFFF")
    st.write("🗨 Wait for the map to load, then click on the desired pickup point to select. Now click the 'Submit' button and repeat these steps again to select the destination point.")

    my_map = folium.Map(location=[41, -73.5], zoom_start=8)

    my_map.add_child(folium.LatLngPopup())
    # folium.TileLayer('Stamen Terrain').add_to(my_map)
    # folium.TileLayer('Stamen Toner').add_to(my_map)
    # folium.TileLayer('Stamen Water Color').add_to(my_map)
    # folium.TileLayer('cartodbpositron').add_to(my_map)
    # folium.TileLayer('cartodbdark_matter').add_to(my_map)
    # folium.LayerControl().add_to(my_map)

    coordinates = json.load(open("temp_coordinates.json"))

    res_map = st_folium(my_map, height=300, width=600)

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
            if target == "c1":
                print_fancy_header(text=f"Latitude: {dropoff_latitude}", font_size=18, color="#52fa23")
                print_fancy_header(text=f"Longitude: {dropoff_longitude}", font_size=18, color="#52fa23")
            else:
                st.write(f"Latitude: {pickup_latitude}")
                st.write(f"Longitude: {pickup_longitude}")
        with col2:
            st.write("🔵 Destination coordinates:")
            if target == "c2":
                print_fancy_header(text=f"Latitude: {dropoff_latitude}", font_size=18, color="#52fa23")
                print_fancy_header(text=f"Longitude: {dropoff_longitude}", font_size=18, color="#52fa23")
            else:
                st.write(f"Latitude: {dropoff_latitude}")
                st.write(f"Longitude: {dropoff_longitude}")


        json.dump(coordinates, open("temp_coordinates.json", "w" ))

        st.write("🗨 Points on the map are updated one by one after clicking")

    except Exception as err:
        print(err)
        pass

    submit_button = st.form_submit_button(label='Submit')


try:
    print_fancy_header('\n🤖 Feature Engineering...')
    df = process_input_vector(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)

    # X features
    X = df.drop(columns=['ride_id', 'taxi_id', 'driver_id', 'pickup_latitude', 'pickup_longitude',
                         'dropoff_latitude', 'dropoff_longitude', 'pickup_datetime'])

    st.dataframe(X)

    st.write(36 * "-")
    print_fancy_header('\n 🤖 Getting the model...')
    model = get_model(project=project, model_name="nyc_taxi_fares_model",
                      file_name="nyc_taxi_fares_model")
    st.write("✅ Done!")

    st.write(36 * "-")
    print_fancy_header('\n🧠 Making price prediction for your trip...')

    prediction = model.predict(X)[0]

    st.subheader(f"Prediction: {str(prediction)} $")

    st.write(36 * "-")

    if st.button('📡 Insert this new data to the Hopsworks Feature Store'):
        st.write("⬆️ Inserting a new data to the 'rides' Feature Group...")
        print("Inserting into RIDES FG.")
        rides_cols = ['ride_id', 'pickup_datetime', 'pickup_longitude', 'dropoff_longitude',
                      'pickup_latitude', 'dropoff_latitude', 'passenger_count', 'taxi_id',
                      'driver_id', 'distance', 'pickup_distance_to_jfk',
                      'dropoff_distance_to_jfk', 'pickup_distance_to_ewr',
                      'dropoff_distance_to_ewr', 'pickup_distance_to_lgr',
                      'dropoff_distance_to_lgr', 'year', 'weekday', 'hour']

        rides_fg.insert(df[rides_cols], write_options={"wait_for_job": False})

        st.write("⬆️ Inserting a new data to the 'fares' Feature Group...")
        print("Inserting into FARES FG.")
        fares_cols = ['tolls', 'taxi_id', 'driver_id', 'ride_id']

        df_fares = df[fares_cols]
        df_fares["total_fare"] = prediction
        for col in ["tolls", "total_fare"]:
            df_fares[col] = df_fares[col].astype("double")

        fares_fg.insert(df_fares, write_options={"wait_for_job": False})

        st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')

except Exception as err:
        print(err)
        pass


st.button("Re-run")
