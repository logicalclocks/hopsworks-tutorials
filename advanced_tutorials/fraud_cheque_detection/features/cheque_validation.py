import pandas as pd

def get_cheque_ids(feature_group, data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a sequence of new cheque IDs for a DataFrame based on the maximum existing cheque ID found in a feature group.

    The function first attempts to find the maximum 'cheque_id' using the feature group statistics.
    If it finds this max ID, it generates a new sequence of cheque IDs for the DataFrame starting from the next integer.
    If it encounters any issue in the process (e.g., the feature group does not exist), it resets the DataFrame's index 
    to create a 'cheque_id' based on the row index.

    Parameters:
        feature_group: Hopsworks Feature Group.
        data (pd.DataFrame): The DataFrame to which the cheque ID will be added.

    Returns:
        pd.DataFrame: The modified DataFrame with a new 'cheque_id' column added.
    """
    try:
        # Extract the maximum 'cheque_id' from feature_group if it exists
        cheque_id_max = [
            int(feature.max) 
            for feature in feature_group.statistics.feature_descriptive_statistics 
            if feature.feature_name == 'cheque_id'
        ][0]
        
        # Generate new cheque IDs starting from the maximum found + 1
        data['cheque_id'] = [*range(cheque_id_max + 1, cheque_id_max + 1 + data.shape[0])]
    
    except Exception as e:
        # In case of any error during ID generation, fallback to using DataFrame index as 'cheque_id'
        data = data.reset_index(drop=False).rename(columns={'index': 'cheque_id'})
    
    return data
