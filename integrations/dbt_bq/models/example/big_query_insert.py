def model(dbt, session):
    # Setup cluster usage
    dbt.config(
        submission_method="cluster",
        dataproc_cluster_name="{YOUR_DATAPROC_CLUSTER_NAME}",
    )

    # Read data_pipeline Python model
    data_pipeline = dbt.ref("data_pipeline")

    # Define the list of columns to drop
    columns_to_drop = ['index_column', 'hour', 'day', 'temperature_diff', 'wind_speed_category']

    # Drop the specified columns
    data_pipeline = data_pipeline.drop(*columns_to_drop)

    # Write data to BigQuery table
    data_pipeline.write.format('bigquery') \
        .option('table', 'weather_data_demo.weather_data_demo_table') \
        .mode('append') \
        .save()

    return data_pipeline