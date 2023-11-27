import numpy as np
import pandas as pd

def generate_fares_data(n_records: int) -> pd.DataFrame:
    """
    Generate a DataFrame with simulated taxi fare data.

    Parameters:
    - n_records (int): Number of records to generate.

    Returns:
    - pd.DataFrame: DataFrame containing simulated taxi fare data with columns:
        - 'taxi_id' (int): Taxi ID.
        - 'driver_id' (int): Driver ID.
        - 'tolls' (int): Tolls for the trip.
        - 'total_fare' (int): Total fare for the trip.
    """
    fares_cols = ['taxi_id', 'driver_id', 'tolls', 'total_fare']
    res = pd.DataFrame(columns=fares_cols)

    for i in range(1, n_records + 1):
        temp_df = pd.DataFrame.from_dict({
            "total_fare": [np.random.randint(3, 250)],
            "tolls": [np.random.randint(0, 6)],
            "taxi_id": [np.random.randint(1, 201)],
            "driver_id": [np.random.randint(1, 201)]
        })

        res = pd.concat([temp_df, res], ignore_index=True)

    return res