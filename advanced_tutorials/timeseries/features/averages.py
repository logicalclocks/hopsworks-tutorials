import pandas as pd


def calculate_second_order_features(df):
    """
    Calculate second-order features based on price data for each unique ID.

    Parameters:
    - df (pd.DataFrame): DataFrame containing price data with 'date', 'id', and 'price' columns.

    Returns:
    - pd.DataFrame: DataFrame with second-order features added for each unique ID.
    """
    # Convert the 'date' column to a datetime object
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort the DataFrame by 'date'
    df = df.sort_values(by=['id', 'date'])
    
    # Create a function to calculate features for each group
    def calculate_features(group):
        # Calculate moving averages for 7 days, 14 days, and 30 days
        group['ma_7'] = group['price'].rolling(window=7).mean()
        group['ma_14'] = group['price'].rolling(window=14).mean()
        group['ma_30'] = group['price'].rolling(window=30).mean()
        
        # Calculate the daily rate of change in prices
        group['daily_rate_of_change'] = group['price'].pct_change() * 100  # Calculate as a percentage change
    
        # Calculate the volatility using standard deviation for a 30-day window
        group['volatility_30_day'] = group['price'].rolling(window=30).std()
        
        # Calculate exponential moving averages (EMA) with smoothing factors 0.2 and 0.5
        group['ema_02'] = group['price'].ewm(alpha=0.2).mean()
        group['ema_05'] = group['price'].ewm(alpha=0.5).mean()
        
        # Calculate RSI
        group['rsi'] = 100 - (100 / (1 + (group['price'].pct_change().rolling(window=14).mean() / 100)))
        
        # Fill missing values with zeros for all columns
        group.fillna(0, inplace=True)
        
        return group
    
    # Apply the calculate_features function to each ID group
    df = df.groupby('id').apply(calculate_features)
    
    # Drop the original 'price' column
    df.drop('price', axis=1, inplace=True)
    
    return df
