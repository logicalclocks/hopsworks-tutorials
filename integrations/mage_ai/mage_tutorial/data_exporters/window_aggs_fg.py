import hopsworks
from mage_ai.data_preparation.shared.secrets import get_secret_value
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def window_aggs_fg_creation(data, *args, **kwargs):
    """
    Creates the transaction window aggregations Feature Group.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)
    """
    # Specify the window length as "4h"
    window_len = "4h" 

    # Specify your data exporting logic here
    project = hopsworks.login(
        api_key_value=get_secret_value('HOPSWORKS_API_KEY'),
        )

    fs = project.get_feature_store()

    # Get or create the 'transactions' feature group with aggregations using specified window len
    window_aggs_fg = fs.get_or_create_feature_group(
        name=f"transactions_{window_len}_aggs",
        version=1,
        description=f"Aggregate transaction data over {window_len} windows.",
        primary_key=["cc_num"],
        event_time="datetime",
        online_enabled=True,
    )

    # Insert data into feature group
    window_aggs_fg.insert(
        data, 
        write_options={"wait_for_job": True},
    )
    
    # Update feature descriptions
    feature_descriptions = [
        {"name": "datetime", "description": "Transaction time"},
        {"name": "cc_num", "description": "Number of the credit card performing the transaction"},
        {"name": "loc_delta_mavg", "description": "Moving average of location difference between consecutive transactions from the same card"},
        {"name": "trans_freq", "description": "Moving average of transaction frequency from the same card"},
        {"name": "trans_volume_mavg", "description": "Moving average of transaction volume from the same card"},
        {"name": "trans_volume_mstd", "description": "Moving standard deviation of transaction volume from the same card"},
    ]

    for desc in feature_descriptions: 
        window_aggs_fg.update_feature_description(desc["name"], desc["description"])



