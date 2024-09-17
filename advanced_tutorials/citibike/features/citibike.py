import requests
from datetime import datetime, timedelta
import zipfile
from io import BytesIO
import os
from calendar import monthrange
import pandas as pd

# Mute warnings
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

"""
Basic functions
"""

def convert_date_to_unix(x: str) -> int:
    """
    Convert a date string to Unix timestamp in milliseconds.

    Parameters:
        x (str): Input date string in the format '%Y-%m-%d'.

    Returns:
        int: Unix timestamp in milliseconds.
    """
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


def convert_unix_to_date(x: int) -> str:
    """
    Convert a Unix timestamp in milliseconds to a date string.

    Parameters:
        x (int): Unix timestamp in milliseconds.

    Returns:
        str: Date string in the format '%Y-%m-%d'.
    """
    x //= 1000
    x = datetime.fromtimestamp(x)
    return datetime.strftime(x, "%Y-%m-%d")


def get_next_date(date: str) -> str:
    """
    Get the next date from the given date.

    Parameters:
        date (str): Input date string in the format '%Y-%m-%d'.

    Returns:
        str: Next date string in the format '%Y-%m-%d'.
    """
    next_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
    return datetime.strftime(next_date, "%Y-%m-%d")


def get_last_date_in_fg(fg) -> str:
    """
    Get the last date in the given feature group.

    Parameters:
        fg: Feature group object.

    Returns:
        str: Last date string in the format '%Y-%m-%d'.
    """
    date_max = [
        int(feature.max)
        for feature in fg.statistics.feature_descriptive_statistics 
        if feature.feature_name == 'timestamp'
    ][0]
    return convert_unix_to_date(date_max)


###############################################################################
# Data basic processing

def select_stations_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select relevant columns for station information and remove duplicates.

    Parameters:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with columns 'station_id', 'station_name', 'lat', and 'long'.
    """
    df_res = df[["start_station_id", "start_station_name", "start_lat", "start_lng"]] \
        .rename(columns={"start_station_id": "station_id",
                         "start_station_name": "station_name",
                         "start_lat": "lat",
                         "start_lng": "long"})
    df_res = df_res.drop_duplicates()
    return df_res


def process_df(original_df: pd.DataFrame, month: str, year: str) -> pd.DataFrame:
    """
    Process the input DataFrame by aggregating users_count for each day and station.

    Parameters:
        original_df (pd.DataFrame): Input DataFrame with columns 'started_at' and 'start_station_id'.
        month (str): Month as a string (e.g., "04").
        year (str): Year as a string (e.g., "2021").

    Returns:
        pd.DataFrame: Processed DataFrame with columns 'date', 'station_id', and 'users_count'.
    """
    df_res = original_df[["started_at", "start_station_id"]]
    df_res.started_at = pd.to_datetime(df_res.started_at)
    df_res.started_at = df_res.started_at.dt.floor('d')
    df_res = (df_res.groupby(['started_at', 'start_station_id'])
              .size()
              .reset_index(name='users_count'))
    df_res = df_res.rename(columns={"started_at": "date",
                                    "start_station_id": "station_id",
                                    0: "users_count"})
    # Select only popular stations
    days_in_month = monthrange(int(year), int(month))[1]
    popular_stations = df_res.station_id.value_counts()[df_res.station_id.value_counts() == days_in_month].index
    df_res = df_res[df_res.station_id.isin(popular_stations)]
    return df_res.sort_values(by=["date", "station_id"])


def update_month_data(main_df: pd.DataFrame, month: str, year: str) -> pd.DataFrame:
    """
    Update the main DataFrame with data for a specific month and year.

    Parameters:
        main_df (pd.DataFrame): Main DataFrame to be updated.
        month (str): Month as a string (e.g., "04").
        year (str): Year as a string (e.g., "2021").

    Returns:
        pd.DataFrame: Updated DataFrame.
    """
    if month < 10:
        month = f"0{month}"
    print(f"_____ Processing {month}/{year}... _____")

    if f"{year}{month}" in ["202206", "202207"]:
        citibike = "citibike"
    else:
        citibike = "citibike"
    url = f'https://s3.amazonaws.com/tripdata/JC-{year}{month}-{citibike}-tripdata.csv.zip'
    print(url)
    filename = "data/" + url.split('/')[-1].split(".")[0] + ".csv"
    fn_list = filename.split(".")
    processed_filename = fn_list[-2] + "_processed." + fn_list[-1]

    if os.path.isfile(processed_filename):
        print("Retrieving DataFrame from the existing csv file...💿")
        return pd.concat([pd.read_csv(processed_filename), main_df])

    print('Downloading Started...⏳')

    req = requests.get(url)

    print('Downloading Completed!👌')

    file= zipfile.ZipFile(BytesIO(req.content))

    file.extractall("data/")

    print("Retrieving DataFrame from the csv file...💿")
    print("-" * 32)

    original_df = pd.read_csv(filename)

    if not os.path.isfile("data/stations_info.csv"):
        stations_info_df = select_stations_info(original_df)
    else:
        present_stations_df = pd.read_csv("data/stations_info.csv")
        stations_info_batch = select_stations_info(original_df)
        stations_info_df = pd.concat([
            present_stations_df,
            stations_info_batch
            ]).reset_index(drop=True)
    stations_info_df.to_csv("data/stations_info.csv", index=False)

    processed_df = process_df(original_df, month, year)

    # Delete original big unprocessed file
    os.remove(filename)

    # Save processed file in csv
    processed_df.to_csv(processed_filename, index=False)

    return pd.concat([processed_df, main_df])


def get_citibike_data(start_date: str = "04/2021", end_date: str = "10/2022") -> pd.DataFrame:
    """
    Retrieve Citibike data for a specified date range.

    Parameters:
        start_date (str): Start date in the format 'MM/YYYY'.
        end_date (str): End date in the format 'MM/YYYY'.

    Returns:
        pd.DataFrame: DataFrame with columns 'date', 'station_id', and 'users_count'.
    """
    start_month, start_year = start_date.split("/")[0], start_date.split("/")[1]
    end_month, end_year = end_date.split("/")[0], end_date.split("/")[1]

    df_res = pd.DataFrame(columns=["date", "station_id", "users_count"])

    if start_year == end_year:
        for month in range(int(start_month), int(end_month) + 1):
            df_res = update_month_data(df_res, month, start_year)

    else:
        for month in range(int(start_month), 12 + 1):
            df_res = update_month_data(df_res, month, start_year)
        for month in range(1, int(end_month) + 1):
            df_res = update_month_data(df_res, month, end_year)

    df_res["users_count"] = df_res["users_count"].astype(int)

    print("\n✅ Done ✅")

    return df_res.reset_index(drop=True)


def moving_average(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """
    Calculate the moving average for 'users_count' grouped by 'station_id' and add the result as a new column.

    Parameters:
        df (pd.DataFrame): Input DataFrame with columns 'date', 'station_id', and 'users_count'.
        window (int): The window size for the rolling mean.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column for the engineered moving average feature.
    """
    result = df.copy()
    result[f'mean_{window}_days'] = result.groupby('station_id')['users_count'].rolling(window=window).mean().reset_index(
        0, 
        drop=True,
    ).shift(1)
    return result


def moving_std(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculate the moving standard deviation for 'users_count' grouped by 'station_id' and add the result as a new column.

    Parameters:
        df (pd.DataFrame): Input DataFrame with columns 'date', 'station_id', and 'users_count'.
        window (int): The window size for the rolling standard deviation.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column for the engineered moving standard deviation feature.
    """
    result = df.copy()
    result[f'moving_std_{window}_days'] = result.groupby('station_id')['users_count'].rolling(window=window).std().reset_index(
        0,
        drop=True,
    ).shift(1)
    return result


def exponential_moving_average(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculate the exponential moving average for 'users_count' grouped by 'station_id' and add the result as a new column.

    Parameters:
        df (pd.DataFrame): Input DataFrame with columns 'date', 'station_id', and 'users_count'.
        window (int): The span parameter for exponential moving average.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column for the engineered exponential moving average feature.
    """
    result = df.copy()
    result[f'exponential_moving_average_{window}_days'] = result.groupby('station_id')['users_count'].ewm(span=window).mean().reset_index(
        0, 
        drop=True,
    ).shift(1)
    return result


def exponential_moving_std(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculate the exponential moving standard deviation for 'users_count' grouped by 'station_id' and add the result as a new column.

    Parameters:
        df (pd.DataFrame): Input DataFrame with columns 'date', 'station_id', and 'users_count'.
        window (int): The span parameter for exponential moving standard deviation.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column for the engineered exponential moving standard deviation feature.
    """
    result = df.copy()
    result[f'exponential_moving_std_{window}_days'] = result.groupby('station_id')['users_count'].ewm(span=window).std().reset_index(
        0, 
        drop=True,
    ).shift(1)
    return result


def engineer_citibike_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer various features for Citibike data and return the resulting DataFrame.

    Parameters:
        df (pd.DataFrame): Input DataFrame with columns 'date', 'station_id', and 'users_count'.

    Returns:
        pd.DataFrame: DataFrame with engineered features including moving averages and standard deviations.
    """
    df_res = df.copy()

    # Remove duplicated rows
    df_res = df_res.groupby(['date', 'station_id'], as_index=False)['users_count'].sum()

    # Add a column for the previous day's 'users_count'
    df_res['prev_users_count'] = df_res.groupby('station_id')['users_count'].shift(+1)
    df_res = df_res.dropna()

    # Add moving averages with window sizes 7 and 14
    df_res = moving_average(df_res, 7)
    df_res = moving_average(df_res, 14)

    # Add various features for window sizes 7 and 14
    for window_size in [7, 14]:
        for func in [moving_std, exponential_moving_average, exponential_moving_std]:
            df_res = func(df_res, window_size)

    return df_res.reset_index(drop=True).sort_values(by=["date", "station_id"]).dropna()