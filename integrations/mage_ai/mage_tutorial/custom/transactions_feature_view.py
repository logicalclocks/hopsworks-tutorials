import hopsworks
from mage_ai.data_preparation.shared.secrets import get_secret_value
if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def transform_custom(*args, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    TEST_SIZE = 0.2
    # Specify the window length as "4h"
    window_len = "4h" 

    # Specify your data exporting logic here
    project = hopsworks.login(
        api_key_value=get_secret_value('HOPSWORKS_API_KEY'),
        )

    fs = project.get_feature_store()

    trans_fg = fs.get_feature_group(
        name="transactions",
        version=1,
    )

    window_aggs_fg = fs.get_feature_group(
        name=f"transactions_{window_len}_aggs",
        version=1,
    )

    # Select features for training data.
    query = trans_fg.select(["fraud_label", "category", "amount", "age_at_transaction", "days_until_card_expires", "loc_delta"])\
        .join(window_aggs_fg.select_except(["cc_num"]))

    # Load transformation functions.
    label_encoder = fs.get_transformation_function(name="label_encoder")

    # Map features to transformations.
    transformation_functions = [
        label_encoder("category"),
    ]

    # Get or create the 'transactions_view' feature view
    feature_view = fs.get_or_create_feature_view(
        name='transactions_view',
        version=1,
        query=query,
        labels=["fraud_label"],
        transformation_functions=transformation_functions,
    )

    return print('✅ Done')  

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
