import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_credit_data(*args, **kwargs):
    # Specify the URL for the data
    url = "https://repo.hops.works/master/hopsworks-tutorials/data/card_fraud_data/"
    # Read the 'credit_cards.csv' file
    credit_cards_df = pd.read_csv(url + "credit_cards.csv")

    return credit_cards_df


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
