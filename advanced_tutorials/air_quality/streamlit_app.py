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

    try:
        new_lat, new_long = res_map["last_clicked"]["lat"], res_map["last_clicked"]["lng"]

        coordinates = {
            "lat": new_lat,
            "long": new_long,
        }

        # display selected points
        
        # print_fancy_header(text=f"Latitude: {new_lat}", font_size=18, color="#52fa23")
        # print_fancy_header(text=f"Longitude: {new_long}", font_size=18, color="#52fa23")
    
        # Calculate the distance between the clicked location and each city
        distances = {city: distance.distance(coord, (new_lat, new_long)).km for city, coord in dict_for_map.items()}

        # Find the city with the minimum distance and print its name
        nearest_city = min(distances, key=distances.get)
        st.write("The nearest city is:", nearest_city)
        # st.write(label_encoder.transform([nearest_city])[0])

    except Exception as err:
        print(err)
        pass

    submit_button = st.form_submit_button(label='Submit')


