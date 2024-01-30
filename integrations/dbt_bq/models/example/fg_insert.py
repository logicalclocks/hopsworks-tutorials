# Import required packages
import hsfs
from pyspark.sql.functions import unix_timestamp

def model(dbt, session):
    # Setup cluster usage
    dbt.config(
        submission_method="cluster",
        dataproc_cluster_name="{YOUR_HOPSWORKS_API_KEY}",
    )

    # Read data_pipeline Python model
    data_pipeline = dbt.ref("data_pipeline")

    # Connect to the Hopsworks feature store
    hsfs_connection = hsfs.connection(
        host="{YOUR_HOST}",
        project="{YOUR_PROJECT_NAME}",
        hostname_verification=False,
        api_key_value="{YOUR_HOPSWORKS_API_KEY}",
        engine='spark',
    )

    # Retrieve the metadata handle
    feature_store = hsfs_connection.get_feature_store()

    # Get or create Feature Group
    feature_group = feature_store.get_or_create_feature_group(
        name = '{YOUR_FEATURE_GROUP_NAME}',
        version = 1,
    )

    # Insert data into Feature Group
    feature_group.insert(data_pipeline)   

    return data_pipeline