import numpy as np
import pandas as pd

import secrets

import hopsworks


# rides data functions
##########################################################################

# # an example of random generated hash
# secrets.token_hex(nbytes=16)

def generate_rides_data(n_records):
    rides_cols = ['ride_id',
                  'pickup_datetime',
                  'pickup_longitude',
                  'pickup_latitude',
                  'dropoff_longitude',
                  'dropoff_latitude',
                  'passenger_count',
                  'taxi_id',
                  'driver_id']

    res = pd.DataFrame(columns=rides_cols)
    
    for i in range(1, n_records + 1):
        generated_values = list()
     
        
        temp_df = pd.DataFrame.from_dict({"ride_id": [secrets.token_hex(nbytes=16)],
                                          "pickup_datetime": [np.random.randint(15778836, 16100000) * 100000],
                                          "pickup_longitude": [round(np.random.uniform(-74.5, -72.8), 5)],
                                          "dropoff_longitude": [round(np.random.uniform(-74.5, -72.8), 5)],
                                          "pickup_latitude": [round(np.random.uniform(40.5, 41.8), 5)],
                                          "dropoff_latitude": [round(np.random.uniform(40.5, 41.8), 5)],
                                          "passenger_count": [np.random.randint(1, 5)],
                                          "taxi_id": [np.random.randint(1, 201)],
                                          "driver_id": [np.random.randint(1, 201)]
                                         })
        
        res = pd.concat([temp_df, res], ignore_index=True)
    
    coord_cols = ['pickup_longitude','dropoff_latitude','dropoff_longitude','pickup_latitude']
    res[coord_cols] = res[coord_cols].astype("float")

    return res


# returns distance in miles
def calculate_distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295 # Pi/180
    a = 0.5 - np.cos((lat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 0.6213712 * 12742 * np.arcsin(np.sqrt(a))


def calculate_distance_features(df):
    df["distance"] = calculate_distance(df["pickup_latitude"], df["pickup_longitude"],
                            df["dropoff_latitude"], df["dropoff_longitude"])

    # Distances to nearby airports
    jfk = (-73.7781, 40.6413)
    ewr = (-74.1745, 40.6895)
    lgr = (-73.8740, 40.7769)

    df['pickup_distance_to_jfk'] = calculate_distance(jfk[1], jfk[0],
                                         df['pickup_latitude'], df['pickup_longitude'])
    df['dropoff_distance_to_jfk'] = calculate_distance(jfk[1], jfk[0],
                                           df['dropoff_latitude'], df['dropoff_longitude'])
    df['pickup_distance_to_ewr'] = calculate_distance(ewr[1], ewr[0],
                                          df['pickup_latitude'], df['pickup_longitude'])
    df['dropoff_distance_to_ewr'] = calculate_distance(ewr[1], ewr[0],
                                           df['dropoff_latitude'], df['dropoff_longitude'])
    df['pickup_distance_to_lgr'] = calculate_distance(lgr[1], lgr[0],
                                          df['pickup_latitude'], df['pickup_longitude'])
    df['dropoff_distance_to_lgr'] = calculate_distance(lgr[1], lgr[0],
                                           df['dropoff_latitude'], df['dropoff_longitude'])
    return df

def calculate_datetime_features(df):
    df["pickup_datetime"] = (pd.to_datetime(df["pickup_datetime"],unit='ms'))

    df['year'] = df.pickup_datetime.apply(lambda t: t.year)
    df['weekday'] = df.pickup_datetime.apply(lambda t: t.weekday())
    df['hour'] = df.pickup_datetime.apply(lambda t: t.hour)
    df["pickup_datetime"] = df["pickup_datetime"].values.astype(np.int64) // 10 ** 6
    
    return df


# fares data functions
##########################################################################
def generate_fares_data(n_records):
    fares_cols = ['taxi_id', 'driver_id',
                  'tolls', 'total_fare']
    
    res = pd.DataFrame(columns=fares_cols)
    
    for i in range(1, n_records + 1):
        generated_values = list()
     
        
        temp_df = pd.DataFrame.from_dict({"total_fare": [np.random.randint(3, 250)],
                                          "tolls": [np.random.randint(0, 6)],
                                          "taxi_id": [np.random.randint(1, 201)],
                                          "driver_id": [np.random.randint(1, 201)]
                                         })
        
        res = pd.concat([temp_df, res], ignore_index=True)
        
        
    return res