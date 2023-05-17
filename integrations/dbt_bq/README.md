## <span style='color:#ff5f27'> 👨🏻‍🏫 DBT Tutorial with BigQuery </span>

### <span style='color:#ff5f27'> 🏡 Cluster setup </span>

To begin with, it's necessary to setup the Dataproc cluster.

You need to configure an external Spark cluster to be able to interact with the Hopsworks Feature Store.

Navigate to **Project Settings** and then **Integrations**. At the bottom of the page you will find necessary files which you need to attach to your Dataproc cluster.

![output](images/sparkConfig.png)

Code to create Dataproc cluster is present in `provision.sh` file.

To make `provision.sh` file executable do the next:

`chmod +x provision.sh`

Fill in your cluster information and then use `./provision.sh` command to start the cluster creation.

### <span style='color:#ff5f27'>📡 DBT Setup </span>

Install the BigQuery adapter running
`pip install dbt-bigquery`

Create a new profile inside your ~/.dbt/profiles.yml file.

```
{YOUR_PROJECT_NAME}:
 target: dev
 outputs:
   dev:
     # Type of DBT connector (BigQuery, Snowflake, etc)
     type: bigquery
     # Authentication method 
     method: service-account-json
     # Your Google Cloud project name
     project: [your-project-id]
     # Your BigQuery dataset name
     dataset: {YOUR_DATASET_NAME}
     threads: 1


     # These fields come from the service account json keyfile
     keyfile_json:
       type: xxx
       project_id: xxx
       private_key_id: xxx
       private_key: xxx
       client_email: xxx
       client_id: xxx
       auth_uri: xxx
       token_uri: xxx
       auth_provider_x509_cert_url: xxx
       client_x509_cert_url: xxx


     # Your Bucket name
     gcs_bucket: {YOUR_BUCKET_NAME}
     # Your Dataproc region
     dataproc_region: {YOUR_DATAPROC_REGION} 
 ```


### <span style='color:#ff5f27'>⚙️ DBT Launch </span>

Fill in `read_bigquery_data.sql` and `data_pipeline.py` files with your information.

Use the next command to run DBT models pipeline:

`dbt run`

You will see the next output:
![output](images/output.png)

> To see the job logs, check your cluster **Job details**.
