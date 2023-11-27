import secrets
import numpy as np
import pandas as pd


def generate_rides_data(n_records: int) -> pd.DataFrame:
    """
    Generate a DataFrame with simulated ride data.

    Parameters:
    - n_records (int): Number of ride records to generate.

    Returns:
    - pd.DataFrame: DataFrame containing simulated ride data with columns:
        - 'ride_id' (str): Ride ID.
        - 'pickup_datetime' (int): Pickup date and time in milliseconds.
        - 'pickup_longitude' (float): Pickup longitude.
        - 'pickup_latitude' (float): Pickup latitude.
        - 'dropoff_longitude' (float): Dropoff longitude.
        - 'dropoff_latitude' (float): Dropoff latitude.
        - 'passenger_count' (int): Number of passengers.
        - 'taxi_id' (int): Taxi ID.
        - 'driver_id' (int): Driver ID.
    """
    rides_cols = ['ride_id', 'pickup_datetime', 'pickup_longitude', 'pickup_latitude',
                  'dropoff_longitude', 'dropoff_latitude', 'passenger_count', 'taxi_id', 'driver_id']
    res = pd.DataFrame(columns=rides_cols)

    for i in range(1, n_records + 1):
        temp_df = pd.DataFrame.from_dict({
            "ride_id": [secrets.token_hex(nbytes=16)],
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

    coord_cols = ['pickup_longitude', 'dropoff_latitude', 'dropoff_longitude', 'pickup_latitude']
    res[coord_cols] = res[coord_cols].astype("float")

    return res


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two sets of coordinates in miles.

    Parameters:
    - lat1 (float): Latitude of the first point.
    - lon1 (float): Longitude of the first point.
    - lat2 (float): Latitude of the second point.
    - lon2 (float): Longitude of the second point.

    Returns:
    - float: Distance between the two points in miles.
    """
    p = 0.017453292519943295  # Pi/180
    a = 0.5 - np.cos((lat2 - lat1) * p) / 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (
            1 - np.cos((lon2 - lon1) * p)) / 2
    return 0.6213712 * 12742 * np.arcsin(np.sqrt(a))


def calculate_distance_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate additional distance-related features for a DataFrame of ride data.

    Parameters:
    - df (pd.DataFrame): DataFrame containing ride data with columns:
        - 'pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude'.

    Returns:
    - pd.DataFrame: DataFrame with additional columns for distance-related features.
    """
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


def calculate_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and calculate additional datetime-related features for a DataFrame of ride data.

    Parameters:
    - df (pd.DataFrame): DataFrame containing ride data with a 'pickup_datetime' column.

    Returns:
    - pd.DataFrame: DataFrame with additional columns for datetime-related features.
    """
    df["pickup_datetime"] = (pd.to_datetime(df["pickup_datetime"], unit='ms'))

    df['year'] = df.pickup_datetime.apply(lambda t: t.year)
    df['weekday'] = df.pickup_datetime.apply(lambda t: t.weekday())
    df['hour'] = df.pickup_datetime.apply(lambda t: t.hour)
    df["pickup_datetime"] = df["pickup_datetime"].values.astype(np.int64) // 10 ** 6

    return df