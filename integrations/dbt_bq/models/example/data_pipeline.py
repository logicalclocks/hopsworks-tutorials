# Import required packages
import hsfs

def model(dbt, session):
    # Setup cluster usage
    dbt.config(
        submission_method="cluster",
        dataproc_cluster_name="YOUR_CLUSTER_NAME",
    )

    # Read BigQuery Data
    my_sql_model_df = dbt.ref("read_bigquery_data")

    # Returns Pyspark DataFrame 
    print(type(my_sql_model_df))

    # Show first 3 rows of data
    print(my_sql_model_df.show(3))

    # Setup your HSFS connection 
    project = hsfs.connection(
        host="YOUR_HOST",
        project="YOUR_PROJECT_NAME",
        api_key_value="YOUR_HOPSWORKS_API_KEY",
    )

    # Retrieve your Feature Store
    fs = project.get_feature_store()   

    # Feature Group creation
    weather_fg = fs.get_or_create_feature_group(
        name = 'weather_fg',
        description = 'Weather data',
        version = 1,
        primary_key = ['index_column'],
        stream = True,
        online_enabled = True,
    )    
    # Insert your data into Feature Group
    weather_fg.insert(my_sql_model_df)   

    return my_sql_model_df