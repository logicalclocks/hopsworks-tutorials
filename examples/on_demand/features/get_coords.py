from geopy.geocoders import Nominatim


lookup = Nominatim(user_agent="long-lat-lookup", scheme='http', timeout=10)

def get_long_lat_from_address(streetName, number, city):
    number = str(int(float(number)))
    address = f'{streetName} {number}, {city}'
    
    if number == '0':
        address = f'{streetName}, {city}'
        
    location = lookup.geocode(address)
    
    # Return with a precision of 3 decimals (accuracy of <110 meter)
    lat = round(location.latitude, 3)
    lon = round(location.longitude, 3)
    return lat, lon


if __name__ == "__main__":
    res = get_long_lat_from_address("Nybohovsbacken", 48, "Stockholm")
    print(res)
