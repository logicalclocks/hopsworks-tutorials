import pandas as pd
import numpy as np
from datetime import date, timedelta
import datetime
from tqdm import tqdm 
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
from typing import List, Union, Optional, Tuple, Dict

def generate_historical_day(date: date, start_date: date, data_list: List[Tuple[datetime.datetime, int, float]]) -> List[Tuple[datetime.datetime, int, float]]:
    """
    Generates synthetic data for a given day with different price patterns for each ID.

    Parameters:
    - date (datetime.date): The date for which data should be generated.
    - start_date (datetime.date): The start date for synthetic data generation.
    - data_list (list): The list to which the generated data should be appended.

    Returns:
    - list: The updated data list containing generated data entries.
    """

    num_entries = 5000  # 5000 rows per day
    ids = np.arange(5001)  # IDs from 0 to 5000

    # Calculate smoother price variations with increased range and seasonality
    days_since_start = (date - start_date).days
    price_base = 200 + 30 * np.sin(2 * np.pi * days_since_start / 365)
    price_variation = (
        10 * np.sin(2 * np.pi * days_since_start / 30) +
        5 * np.sin(2 * np.pi * days_since_start / 7)  # Weekly pattern
    )

    # Generate a range of prices based on the calculated variations
    prices = np.linspace(price_base - price_variation, price_base + price_variation, num_entries)

    # Convert date to datetime at midnight for timestamp compatibility
    datetime_val = datetime.datetime.combine(date, datetime.time())

    for _ in range(num_entries):
        # Randomly select an ID from the list of IDs
        selected_id = np.random.choice(ids)
        # Ensure non-negative prices
        price = max(prices[_], 0)
        # Append the generated data entry to the data list
        data_list.append((datetime_val, selected_id, round(price, 1)))

    return data_list


def generate_historical_data(start_date: Optional[date] = None, end_date: Optional[date] = None) -> pd.DataFrame:
    """
    Generates synthetic data for a range of dates with different price patterns for each ID.

    Parameters:
    - start_date (datetime.date, optional): The start date for the data generation. Default is today's date.
    - end_date (datetime.date, optional): The end date for the data generation. Default is today's date.

    Returns:
    - pd.DataFrame: A DataFrame containing the generated data with columns ['date', 'id', 'price'].
    """
    if start_date is None:
        start_date = datetime.date.today()
    if end_date is None:
        end_date = datetime.date.today()
    
    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        
    data_list = []
    
    for date in tqdm(date_range, desc="🔮 Generating Data"):
        generate_historical_day(date, start_date, data_list)
    
    df = pd.DataFrame(data_list, columns=['date', 'id', 'price'])
    
    # Ensure date column is datetime type for timestamp compatibility
    df['date'] = pd.to_datetime(df['date'])
    
    df.drop_duplicates(inplace=True)

    return df


def generate_today() -> pd.DataFrame:
    """
    Generate random data for the current date and return it as a pandas DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame containing data for the current date, including date,
                          selected ID, and a random price value.
    """
    num_entries = 5000  # 5000 rows per day
    ids = np.arange(5001)  # IDs from 0 to 5000
    data_list = []
    
    # Use datetime instead of date for timestamp compatibility
    current_datetime = datetime.datetime.combine(datetime.date.today(), datetime.time())
    
    prices = (
        200 + np.random.uniform(-50, 50, num_entries)
    )
    
    for entry in range(num_entries):
        selected_id = np.random.choice(ids)
        data_list.append((current_datetime, selected_id, round(prices[entry], 1)))
        
    df = pd.DataFrame(data_list, columns=['date', 'id', 'price'])
    
    # Ensure date column is datetime type for timestamp compatibility
    df['date'] = pd.to_datetime(df['date'])
    
    df.drop_duplicates(inplace=True)

    return df


def to_wide_format(data: pd.DataFrame) -> pd.DataFrame:
    """
    Converts a DataFrame with time series data into wide format.

    Parameters:
    - data (pd.DataFrame): The input DataFrame containing time series data with columns ['date', 'id', 'price'].

    Returns:
    - pd.DataFrame: A DataFrame in wide format with 'date' as the index, 'id' as columns, and 'price' values.
    """
    # Convert the 'date' column to datetime type
    data['date'] = pd.to_datetime(data['date'])

    # Aggregate duplicate entries by taking the mean of prices
    agg_df = data.groupby(['date', 'id'])['price'].mean().reset_index()

    # Pivot the aggregated DataFrame into wide format
    pivoted_df = agg_df.pivot_table(index='date', columns='id', values='price', fill_value=None)

    # Sort the columns in ascending order
    pivoted_df = pivoted_df.sort_index(axis=1)

    # Reset the index to make 'date' a regular column
    pivoted_df.reset_index(inplace=True)

    return pivoted_df


def plot_historical_id(ids_to_show: List[int], data: pd.DataFrame) -> go.Figure:
    """
    Plots time series data for a specified list of IDs.

    Parameters:
    - ids_to_show (list): A list of IDs for which time series data should be plotted.
    - data (pd.DataFrame): The DataFrame containing the data to be plotted, with columns ['date', 'id', 'price'].

    Returns:
    - Figure
    """
    # Filter the DataFrame to include only the specified IDs
    filtered_df = data[data['id'].isin(ids_to_show)]

    # Convert the 'date' column to datetime type
    filtered_df['date'] = pd.to_datetime(filtered_df['date'], format='%Y-%m-%d')
    filtered_df.sort_values('date', inplace=True)

    # Generate a colormap with distinct colors based on the number of unique IDs
    unique_ids = filtered_df['id'].unique()
    num_ids = len(unique_ids)
    colors = pc.qualitative.Set1 * (num_ids // len(pc.qualitative.Set1) + 1)

    # Create a dictionary to map IDs to colors
    color_map = dict(zip(unique_ids, colors[:num_ids]))

    # Create a time series plot using Plotly Express
    fig = px.line(
        filtered_df, 
        x='date', 
        y='price', 
        color='id',
        title=f'Historical Prices for {ids_to_show} IDs',
        labels={'date': 'Date', 'price': 'Price'},
        line_group='id',
        color_discrete_map=color_map,
    )

    return fig


def plot_prediction_test(
    id_to_show: int, 
    X_train: pd.DataFrame, 
    X_test: pd.DataFrame, 
    y_train: Union[pd.Series, pd.DataFrame], 
    y_test: Union[pd.Series, pd.DataFrame], 
    train_date: pd.Series, 
    test_date: pd.Series,
    predictions: Optional[pd.Series] = None
) -> go.Figure:
    """
    Plots a time series for a specific ID, showing training and test data on the same plot.

    Parameters:
    - id_to_show (int): The ID to be displayed in the plot.
    - X_train (pd.DataFrame): The feature data for the training set.
    - X_test (pd.DataFrame): The feature data for the test set.
    - y_train (pd.Series or pd.DataFrame): The target data for the training set.
    - y_test (pd.Series or pd.DataFrame): The target data for the test set.
    - train_date (pd.Series): The date column for the training data.
    - test_date (pd.Series): The date column for the test data.
    - predictions (pd.Series or None): Predicted values for the test data. Default is None.

    Returns:
    - Figure
    """
    # Combine features and target data for training and test sets
    train = pd.concat([train_date, X_train, y_train], axis=1)
    test = pd.concat([test_date, X_test, y_test], axis=1)
    
    # Filter and sort data for the specified ID
    train_sorted = train[train.id == id_to_show].sort_values('date')
    test_sorted = test[test.id == id_to_show].sort_values('date')

    # Create a Plotly figure
    fig = go.Figure()
    
    # Add a trace for training data (blue)
    fig.add_trace(go.Scatter(
        x=train_sorted['date'], 
        y=train_sorted['price'],
        mode='lines',
        name='Training Data',  
        line=dict(color='blue')
    ))
    
    # Add a trace for test data (red)
    fig.add_trace(go.Scatter(
        x=test_sorted['date'], 
        y=test_sorted['price'],
        mode='lines',
        name='Test Data', 
        line=dict(color='green')
    ))
    
    if predictions is not None:
        pred_df = pd.DataFrame()
        pred_df['date'] = test_sorted['date']
        pred_df['price'] = predictions
        fig.add_trace(go.Scatter(
            x=pred_df['date'], 
            y=pred_df['price'],
            mode='lines',
            name='Prediction', 
            line=dict(color='red')
        ))
        
    
    # Set X-axis range to span the entire date range from both training and test data
    fig.update_xaxes(range=[train_sorted['date'].min(), test_sorted['date'].max()])
    
    # Customize plot layout
    fig.update_layout(
        title=f'Time Series for the {id_to_show} ID',
        xaxis_title='Date',
        yaxis_title='Price',
        legend_title='Data Type'
    )

    return fig


def plot_prediction(
    id_to_show: int, 
    data: pd.DataFrame,
    week_ago: str,
    predictions: Optional[pd.Series] = None,
) -> go.Figure:
    """
    Display a time series plot for a specific ID, showcasing historical data, real prices, and predicted prices.

    Parameters:
    - id_to_show (int): The unique identifier for the data series to be displayed.
    - data (pd.DataFrame): A DataFrame containing time series data.
    - week_ago (str): A string representing a date one week ago (in 'YYYY-MM-DD' format).
    - predictions (pd.Series or None, optional): Predicted price values for the test data. Default is None.

    Returns:
    - fig (plotly.graph_objs.Figure): A Plotly figure object containing the generated time series plot.
    """
    data_sorted = data[data.id == id_to_show].sort_values('date')
    data_sorted['date'] = pd.to_datetime(data_sorted['date'])

    time_ago = (datetime.datetime.strptime(week_ago, '%Y-%m-%d') - timedelta(days=210)).strftime("%Y-%m-%d")
    data_historical = data_sorted.loc[
        (data_sorted['date'] <= datetime.datetime.strptime(week_ago, "%Y-%m-%d")) &
        (data_sorted['date'] >= datetime.datetime.strptime(time_ago, "%Y-%m-%d"))
    ]
    data_last_week = data_sorted[data_sorted.date > week_ago]

    # Create a Plotly figure
    fig = go.Figure()
    
    # Add a trace for training data (blue)
    fig.add_trace(go.Scatter(
        x=data_historical['date'], 
        y=data_historical['price'],
        mode='lines',
        name='Historical Data',  
        line=dict(color='blue')
    ))
    
    # Add a trace for test data (red)
    fig.add_trace(go.Scatter(
        x=data_last_week['date'], 
        y=data_last_week['price'],
        mode='lines',
        name='Real Price', 
        line=dict(color='green')
    ))
    
    if predictions is not None:
        pred_df = pd.DataFrame()
        pred_df['date'] = data_last_week['date']
        pred_df['price'] = predictions
        fig.add_trace(go.Scatter(
            x=pred_df['date'], 
            y=pred_df['price'],
            mode='lines',
            name='Predicted Price', 
            line=dict(color='red')
        ))
        
    
    # Set X-axis range to span the entire date range from both training and test data
    fig.update_xaxes(range=[data_historical['date'].min(), data_last_week['date'].max()])
    
    # Customize plot layout
    fig.update_layout(
        title=f'Predicted price for the {id_to_show} ID',
        xaxis_title='Date',
        yaxis_title='Price',
        legend_title='Data Type'
    )

    return fig