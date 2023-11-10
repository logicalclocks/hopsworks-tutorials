import pandas as pd

def predict_id(id_value, data, model):
    """
    Make predictions for a specific ID.

    Parameters:
    - id_value (int): The unique identifier for the data series to be predicted.
    - data (pd.DataFrame): A DataFrame containing the input data with columns including 'id'.
    - model: A machine learning model capable of making predictions on data.

    Returns:
    - preds: Predicted values for the specified ID
    """
    data_filtered = data[data.id == id_value]
    preds = model.predict(data_filtered)
    return preds


def to_df(feature_vector):
    """
    Convert a list of feature vectors or a single feature vector into a Pandas DataFrame.

    Parameters:
    - feature_vector (list or list of lists): A feature vector or a list of feature vectors.

    Returns:
    - data (pd.DataFrame)
    """
    # Check if the input is a list of feature vectors
    if isinstance(feature_vector[0], list): 
        ids = [vector[1] for vector in feature_vector]
        ma_7 = [vector[2] for vector in feature_vector]
        ma_14 = [vector[3] for vector in feature_vector]
        ma_30 = [vector[4] for vector in feature_vector]
        daily_rate_of_change = [vector[5] for vector in feature_vector]
        volatility_30_day = [vector[6] for vector in feature_vector]
        ema_02 = [vector[7] for vector in feature_vector]
        ema_05 = [vector[8] for vector in feature_vector]
        rsi = [vector[9] for vector in feature_vector]
        
        # Create a DataFrame with 'city_name' and 'pm2_5' columns from the lists
        data = pd.DataFrame(
            {
                'id': ids,
                'ma_7': ma_7,
                'ma_14': ma_14,
                'ma_30': ma_30,
                'daily_rate_of_change': daily_rate_of_change,
                'volatility_30_day': volatility_30_day,
                'ema_02': ema_02,
                'ema_05': ema_05,
                'rsi': rsi,
            }
        )
        
        # Return the DataFrame representing multiple feature vectors
        return data

    # If only one feature vector is provided, create a DataFrame for it
    data = pd.DataFrame(
            {
                'id': [feature_vector[1]],
                'ma_7': [feature_vector[2]],
                'ma_14': [feature_vector[3]],
                'ma_30': [feature_vector[4]],
                'daily_rate_of_change': [feature_vector[5]],
                'volatility_30_day': [feature_vector[6]],
                'ema_02': [feature_vector[7]],
                'ema_05': [feature_vector[8]],
                'rsi': [feature_vector[9]],
            }
        )
    
    # Return the DataFrame representing a single feature vector
    return data