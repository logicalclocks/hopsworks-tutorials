import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json
import time


progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.title('🚖NYC Taxi Fares Project🚖')
st.write(36 * "-")
st.header('\n📡 Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()
progress_bar.progress(20)
st.subheader("Successfully connected!✔️")

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
    df = pd.DataFrame.from_dict({ "pickup_datetime": [np.random.randint(1600000000, 1610000000)],
                                          "pickup_longitude": [pickup_longitude],
                                          "dropoff_longitude": [dropoff_longitude],
                                          "pickup_latitude": [pickup_latitude],
                                          "dropoff_latitude": [dropoff_latitude],
                                          "passenger_count": [np.random.randint(1, 5)]
                                         })
     # returns distance in miles
    def distance(lat1, lon1, lat2, lon2):
        p = 0.017453292519943295 # Pi/180
        a = 0.5 - np.cos((lat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
        return 0.6213712 * 12742 * np.arcsin(np.sqrt(a))

    df["distance"] = distance(df["pickup_latitude"], df["pickup_longitude"],
                            df["dropoff_latitude"], df["dropoff_longitude"])

    # Distances to nearby airports
    jfk = (-73.7781, 40.6413)
    ewr = (-74.1745, 40.6895)
    lgr = (-73.8740, 40.7769)

    df['pickup_distance_to_jfk'] = distance(jfk[1], jfk[0],
                                         df['pickup_latitude'], df['pickup_longitude'])
    df['dropoff_distance_to_jfk'] = distance(jfk[1], jfk[0],
                                           df['dropoff_latitude'], df['dropoff_longitude'])
    df['pickup_distance_to_ewr'] = distance(ewr[1], ewr[0],
                                          df['pickup_latitude'], df['pickup_longitude'])
    df['dropoff_distance_to_ewr'] = distance(ewr[1], ewr[0],
                                           df['dropoff_latitude'], df['dropoff_longitude'])
    df['pickup_distance_to_lgr'] = distance(lgr[1], lgr[0],
                                          df['pickup_latitude'], df['pickup_longitude'])
    df['dropoff_distance_to_lgr'] = distance(lgr[1], lgr[0],
                                           df['dropoff_latitude'], df['dropoff_longitude'])

    df["pickup_datetime"] = (pd.to_datetime(df["pickup_datetime"],unit='ms'))

    df['year'] = df.pickup_datetime.apply(lambda t: t.year)
    df['weekday'] = df.pickup_datetime.apply(lambda t: t.weekday())
    df['hour'] = df.pickup_datetime.apply(lambda t: t.hour)
    df["pickup_datetime"] = df["pickup_datetime"].values.astype(np.int64) // 10 ** 6

    return df.drop(columns=['pickup_latitude', 'pickup_longitude',
                            'dropoff_latitude', 'dropoff_longitude',
                            'pickup_datetime'])


st.write(36 * "-")
st.header('\n🧩 Interactive predictions...')
st.subheader("🔺 Please enter the coordinates of the pick-up (click on the map and wait couple of seconds):")
# st.write("**🌇 NYC coordinates: Latitude - (40.5, 41.8), Longitude - (-74.5, -72.8)**")

my_map = folium.Map(location=[41, -73.5], zoom_start=8)

my_map.add_child(folium.LatLngPopup())

coordinates = json.load(open("temp_coordinates.json"))

# folium.Marker(
#       location=[lat, long],
#       popup="text",
#    ).add_to(my_map)

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
# st.subheader("🔻 Please enter the coordinates of the destination:")
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

    # this code will display streamlit map with two selected points
    # map_df = pd.DataFrame(
    #         [[pickup_latitude, pickup_longitude], [dropoff_latitude, dropoff_longitude]],
    #         columns=['lat', 'lon'])
    # st.map(map_df)

    progress_bar.progress(45)

    st.write(36 * "-")
    st.header('\n🤖 Feature Engineering...')
    data = process_input_vector(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)
    st.dataframe(data)
    progress_bar.progress(60)

    st.write(36 * "-")
    st.header('\n🧠 Making price prediction for your trip...')
    model = get_model()
    progress_bar.progress(75)
    preds = model.predict(data)[0]

    st.subheader(f"Prediction: **{str(preds)}**")
    progress_bar.progress(100)

    st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')


except:
    pass

st.button("Re-run")
