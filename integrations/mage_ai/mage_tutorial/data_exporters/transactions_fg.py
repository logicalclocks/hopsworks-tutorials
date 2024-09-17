import hopsworks
from mage_ai.data_preparation.shared.secrets import get_secret_value
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def transaction_fg_creation(data, *args, **kwargs):
    """
    Creates the transaction Feature Group.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)
    """
    project = hopsworks.login(
        api_key_value=get_secret_value('HOPSWORKS_API_KEY'),
        )

    fs = project.get_feature_store()

    # Get or create the 'transactions' feature group
    trans_fg = fs.get_or_create_feature_group(
        name="transactions",
        version=1,
        description="Transaction data",
        primary_key=["cc_num"],
        event_time="datetime",
        online_enabled=True,
    )
    # Insert data into feature group
    trans_fg.insert(data)

    # Update feature descriptions
    feature_descriptions = [
        {"name": "tid", "description": "Transaction id"},
        {"name": "datetime", "description": "Transaction time"},
        {"name": "cc_num", "description": "Number of the credit card performing the transaction"},
        {"name": "category", "description": "Expense category"},
        {"name": "amount", "description": "Dollar amount of the transaction"},
        {"name": "latitude", "description": "Transaction location latitude"},
        {"name": "longitude", "description": "Transaction location longitude"},
        {"name": "city", "description": "City in which the transaction was made"},
        {"name": "country", "description": "Country in which the transaction was made"},
        {"name": "fraud_label", "description": "Whether the transaction was fraudulent or not"},
        {"name": "age_at_transaction", "description": "Age of the card holder when the transaction was made"},
        {"name": "days_until_card_expires", "description": "Card validity days left when the transaction was made"},
        {"name": "loc_delta", "description": "Haversine distance between this transaction location and the previous transaction location from the same card"},
    ]

    for desc in feature_descriptions: 
        trans_fg.update_feature_description(desc["name"], desc["description"])
