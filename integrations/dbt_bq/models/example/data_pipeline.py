# Import required packages
import hopsworks

def model(dbt, session):
    # Setup cluster usage
    dbt.config(
        submission_method="cluster",
        dataproc_cluster_name="dbt-hops",
    )

    # Read read_bigquery_data SQL model
    my_sql_model_df = dbt.ref("read_bigquery_data")

    # Returns Pyspark DataFrame
    print(type(my_sql_model_df))

    # Convert PySpark DataFrame to Pandas DataFrame
    df_pandas = my_sql_model_df.toPandas()

    # Feature Engineering
    df_pandas.reset_index(inplace=True)

    # Print first 5 rows of DataFrame
    print(df_pandas.head())

    # Login to your Hopsworks project
    project = hopsworks.login(
        host="staging.cloud.hopsworks.ai",                                           # DNS of your Feature Store instance
        project="tutorials",                                                                                       # Name of your Hopsworks Feature Store project
        api_key_value="FHQmUY0JVk5aJy6y.Iuk4WoafNKtqDmVHaVGDz7LLe68HIpqqY8seoRWqCEkVaDhC1lzIqJgz7bYDjeMQ"          # Feature store API key value 
    )

    # Get feature Store
    fs = project.get_feature_store()   

    # Get or create Feature Group
    feature_group = fs.get_or_create_feature_group(
        name = 'feature_group_name',
        description = 'Feature Group description',
        version = 1,
        primary_key = ['index_column'],
        online_enabled = True,
    )    

    # Insert data into Feature Group
    feature_group.insert(df_pandas)   

    return my_sql_model_df