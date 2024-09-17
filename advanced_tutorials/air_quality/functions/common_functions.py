import datetime
from geopy.geocoders import Nominatim


def convert_date_to_unix(x):
    """
    Convert datetime to unix time in milliseconds.
    """
    dt_obj = datetime.datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    dt_obj = int(dt_obj.timestamp() * 1000)
    return dt_obj


def get_city_coordinates(city_name: str):
    """
    Takes city name and returns its latitude and longitude (rounded to 2 digits after dot).
    """ 
    # Initialize Nominatim API (for getting lat and long of the city)
    geolocator = Nominatim(user_agent="MyApp")
    city = geolocator.geocode(city_name)

    latitude = round(city.latitude, 2)
    longitude = round(city.longitude, 2)
    
    return latitude, longitude