import numpy as np
import pandas as pd


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