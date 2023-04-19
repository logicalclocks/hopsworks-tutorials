import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy import distance
import json
import time
import pickle

def print_fancy_header(text, font_size=22, color="#ff5f27"):
    res = f'<span style="color:{color}; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )

def save_selected_cities(selected_cities):
    with open("selected_cities.pkl", "wb") as f:
        pickle.dump(selected_cities, f)

def load_selected_cities():
    try:
        with open("selected_cities.pkl", "rb") as f:
            selected_cities = pickle.load(f)
    except:
        selected_cities = []
    return selected_cities

selected_cities = load_selected_cities()
print("Loaded selected_cities.pkl")


st.title('🌫  Air Quality Prediction Project 🌦')

with open('target_cities.json') as json_file:
    target_cities = json.load(json_file)

dict_for_map = {}
for continent in target_cities:
    for city_name, coords in target_cities[continent].items():
        dict_for_map[city_name] = coords

with st.form(key="user_inputs"):
    print_fancy_header(text='\nHere you can choose which city to process.',
                       font_size=24, color="#00FFFF")
    st.write("🗨 Wait for the map to load, then click on the desired city to select. Now click the 'Submit' button.")

    my_map = folium.Map(location=[42.57, -44.092], zoom_start=2)

    # Add markers for each city
    for city_name, coords in dict_for_map.items():
        folium.CircleMarker(
            location=coords,
            popup=city_name
        ).add_to(my_map)

    my_map.add_child(folium.LatLngPopup())

    res_map = st_folium(my_map, width=640, height=480)

    selected_cities_menu = st.multiselect(label='Selected cities:',
                                 options=dict_for_map.keys(),
                                 default=[])

    if not selected_cities:
        st.write("No cities selected yet.")
        

    try:
        new_lat, new_long = res_map["last_clicked"]["lat"], res_map["last_clicked"]["lng"]

        coordinates = {
            "lat": new_lat,
            "long": new_long,
        }

        # Calculate the distance between the clicked location and each city
        distances = {city: distance.distance(coord, (new_lat, new_long)).km for city, coord in dict_for_map.items()}

        # Find the city with the minimum distance and print its name
        nearest_city = min(distances, key=distances.get)
        st.write("The nearest city is:", nearest_city)

        if nearest_city not in selected_cities:
            selected_cities.append(nearest_city)
            save_selected_cities(selected_cities)
        st.write("Selected cities:")
        final_selected_cities = list(set(selected_cities + selected_cities_menu))

        st.write(final_selected_cities)

    except Exception as err:
        print(err)
        pass

    submit_button = st.form_submit_button(label='Submit')
