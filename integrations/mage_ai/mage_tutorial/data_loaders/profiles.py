import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_profiles_data(*args, **kwargs):
    # Specify the URL for the data
    url = "https://repo.hops.works/master/hopsworks-tutorials/data/card_fraud_data/"

    # Read the 'profiles.csv' file
    # Parse the 'birthdate' column as dates
    profiles_df = pd.read_csv(
        url + "profiles.csv", 
        parse_dates=["birthdate"],
        )

    return profiles_df


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
