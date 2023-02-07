import geopy


def coord2zipcode(x):
    geolocator = geopy.Nominatim(user_agent="house_profile_1")
    location = geolocator.reverse("{}, {}".format(x['latitude'], x['longitude']))
    if 'address' in location.raw:
        if 'postcode' in location.raw['address']:
            return int(location.raw['address']['postcode'])
        else:
            return 0
    else:
        return 0
