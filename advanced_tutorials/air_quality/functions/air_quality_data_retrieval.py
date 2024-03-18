import pandas as pd
from typing import Any, Dict, List
import datetime
import pandas as pd


def transform_data(data, encoder):
    """
    Transform the input data by encoding the 'city_name' column and dropping unnecessary columns.
    
    Args:
    - data (DataFrame): Input data to be transformed.
    - encoder (LabelEncoder): Label encoder object to encode 'city_name'.
    
    Returns:
    - data_transformed (DataFrame): Transformed data with 'city_name_encoded' and dropped columns.
    """
    
    # Create a copy of the input data to avoid modifying the original data
    data_transformed = data.copy()
    
    # Transform the 'city_name' column in the batch data using the retrieved label encoder
    data_transformed['city_name_encoded'] = encoder.transform(data_transformed['city_name'])
    
    # Drop unnecessary columns from the batch data
    data_transformed = data_transformed.drop(columns=['unix_time', 'pm2_5', 'city_name', 'date'])

    return data_transformed


def get_data_for_date(date: str, city_name: str, feature_view, model, encoder) -> pd.DataFrame:
    """
    Retrieve data for a specific date and city from a feature view.

    Args:
        date (str): The date in the format "%Y-%m-%d".
        city_name (str): The name of the city to retrieve data for.
        feature_view: The feature view object.
        model: The machine learning model used for prediction.
        encoder (LabelEncoder): Label encoder object to encode 'city_name'.

    Returns:
        pd.DataFrame: A DataFrame containing data for the specified date and city.
    """
    # Convert date string to datetime object
    date_datetime = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    
    # Retrieve batch data for the specified date range
    batch_data = feature_view.get_batch_data(
        start_time=date_datetime,
        end_time=date_datetime + datetime.timedelta(days=1),
    )
    
    # Filter batch data for the specified city
    batch_data_filtered = batch_data[batch_data['city_name'] == city_name]
    
    return batch_data_filtered[['date', 'pm2_5']].sort_values('date').reset_index(drop=True)


def get_data_in_date_range(date_start: str, date_end: str, city_name: str, feature_view, model, encoder) -> pd.DataFrame:
    """
    Retrieve data for a specific date range and city from a feature view.

    Args:
        date_start (str): The start date in the format "%Y-%m-%d".
        date_end (str): The end date in the format "%Y-%m-%d".
        city_name (str): The name of the city to retrieve data for.
        feature_view: The feature view object.
        model: The machine learning model used for prediction.
        encoder (LabelEncoder): Label encoder object to encode 'city_name'.

    Returns:
        pd.DataFrame: A DataFrame containing data for the specified date range and city.
    """
    # Convert date strings to datetime objects
    date_start_dt = datetime.datetime.strptime(date_start, "%Y-%m-%d").date()
    date_end_dt = datetime.datetime.strptime(date_end, "%Y-%m-%d").date()
    
    # Retrieve batch data for the specified date range
    batch_data = feature_view.get_batch_data(
        start_time=date_start_dt,
        end_time=date_end_dt + datetime.timedelta(days=1),
    )

    # Filter batch data for the specified city
    batch_data_filtered = batch_data[batch_data['city_name'] == city_name]
    
    return batch_data_filtered[['date', 'pm2_5']].sort_values('date').reset_index(drop=True)


def get_future_data(date: str, city_name: str, feature_view, model, encoder) -> pd.DataFrame:
    """
    Predicts future PM2.5 data for a specified date and city using a given feature view and model.

    Args:
        date (str): The target future date in the format 'YYYY-MM-DD'.
        city_name (str): The name of the city for which the prediction is made.
        feature_view: The feature view used to retrieve batch data.
        model: The machine learning model used for prediction.
        encoder (LabelEncoder): Label encoder object to encode 'city_name'.

    Returns:
        pd.DataFrame: A DataFrame containing predicted PM2.5 values for each day starting from the target date.

    """
    # Get today's date
    today = datetime.date.today()

    # Convert the target date string to a datetime object
    date_in_future = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    # Calculate the difference in days between today and the target date
    difference_in_days = (date_in_future - today).days

    # Retrieve batch data for the specified date range
    batch_data = feature_view.get_batch_data(
        start_time=today,
        end_time=today + datetime.timedelta(days=1),
    )
    
    # Filter batch data for the specified city
    batch_data_filtered = batch_data[batch_data['city_name'] == city_name]
        
    # Transform batch data
    batch_data_transformed = transform_data(batch_data_filtered, encoder)
    
    # Initialize a DataFrame to store predicted PM2.5 values
    try:
        pm2_5_value = batch_data_filtered['pm2_5'].values[0]
    except (IndexError, TypeError):
        # If accessing pm2_5 values fails, return a message indicating the feature pipeline needs updating
        return "Data is not available. Ask user to run the feature pipeline to update data."
    else:
        # Initialize a DataFrame to store predicted PM2.5 values
        predicted_pm2_5_df = pd.DataFrame({
            'date': [today.strftime("%Y-%m-%d")],
            'pm2_5': pm2_5_value,
        })

    # Iterate through each day starting from tomorrow up to the target date
    for day_number in range(1, difference_in_days + 1):

        # Calculate the date for the current future day
        date_future_day = (today + datetime.timedelta(days=day_number)).strftime("%Y-%m-%d")
        
        # Predict PM2.5 for the current day
        predicted_pm2_5 = model.predict(batch_data_transformed)

        # Update previous day PM2.5 values in the batch data for the next prediction
        batch_data_transformed['pm_2_5_previous_7_day'] = batch_data_transformed['pm_2_5_previous_6_day']
        batch_data_transformed['pm_2_5_previous_6_day'] = batch_data_transformed['pm_2_5_previous_5_day']
        batch_data_transformed['pm_2_5_previous_5_day'] = batch_data_transformed['pm_2_5_previous_4_day']
        batch_data_transformed['pm_2_5_previous_4_day'] = batch_data_transformed['pm_2_5_previous_3_day']
        batch_data_transformed['pm_2_5_previous_3_day'] = batch_data_transformed['pm_2_5_previous_2_day']
        batch_data_transformed['pm_2_5_previous_2_day'] = batch_data_transformed['pm_2_5_previous_1_day']
        batch_data_transformed['pm_2_5_previous_1_day'] = predicted_pm2_5
        
        # Append the predicted PM2.5 value for the current day to the DataFrame
        predicted_pm2_5_df = predicted_pm2_5_df._append({
            'date': date_future_day, 
            'pm2_5': predicted_pm2_5[0],
        }, ignore_index=True)
        
    return predicted_pm2_5_df
