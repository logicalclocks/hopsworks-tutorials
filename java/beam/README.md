# Real time feature computation using Apache Beam, Google Cloud Dataflow and Hopsworks Feature Store

## Introduction
In this guide you will learn how to create Real-Time Feature Engineering pipeline and write real time features in to
the Hopsworks features store. This guide covers creating a

- computing real time features with Apache Beam using Google Cloud Dataflow.
- writing real time features to Hopsworks's online feature store using `hsfs-beam` library.

You will also
- create feature group using the HSFS APIs.
- Backfill feature data to offline feature group.

## Before you begin
For the tutorials to work, you need:
- Hopsworks account
[managed.hopsworks.ai](https://managed.hopsworks.ai) account or on premise Hopsworks deployment. Note that this tutorial 
will not work for [app.hopsworks.ai](https://app.hopsworks.ai) account as submitting custom jobs to 
[app.hopsworks.ai](https://app.hopsworks.ai) are not supported.

You can find documentation how to get started on [GCP](https://docs.hopsworks.ai/3.1/setup_installation/gcp/getting_started/),
[AWS](https://docs.hopsworks.ai/3.1/setup_installation/aws/getting_started/) or on [Azure](https://docs.hopsworks.ai/3.1/setup_installation/azure/getting_started/).

- Google Cloud CLI
- Google Cloud account
- Google Cloud project enabled with Compute Engine, Dataflow, Pub/Sub and Cloud Scheduler APIs:

You also need to have configured maven; java 1.8 and git.

## Clone tutorials repository
```bash
git clone https://github.com/logicalclocks/hopsworks-tutorials
cd ./hopsworks-tutorials/java
mvn clean package
```

## Create Feature Groups
Currently, Beam support for Hopsworks feature store is experimental and only write operation is supported. This means
that Feature group metadata needs to be registered in Hopsworks Feature store before you can write real time features computed
by Beam.

Full documentation how to create feature group using HSFS APIs can be found [here](https://docs.hopsworks.ai/3.1/user_guides/fs/feature_group/create/).

This tutorial comes with notebook to create feature group:
- `. /hopsworks-tutorials/java/beam/setup/1_create_taxi_feature_group.ipynb`

You can execute this notebook directly on Hopsworks cluster. Follow the documentation how to run [spark notebooks](https://docs.hopsworks.ai/3.1/user_guides/projects/jupyter/spark_notebook/)
and [python notebooks](https://docs.hopsworks.ai/3.1/user_guides/projects/jupyter/python_notebook/).

## Data source
Feature pipeline needs to connect to some data source to read the data to be processed. In this tutorial you will
use publicly available topic `projects/pubsub-public-data/topics/taxirides-realtime`

## Start Beam/DataFlow streaming pipeline:

### Google Cloud Pub/Sub to Google Cloud Storage
Now you ready to run a streaming pipeline using Beam and Google Cloud Dataflow. For this you need to
have Hopsworks cluster host address, hopsworks project name and [api key](https://docs.hopsworks.ai/3.1/user_guides/projects/api_key/create_api_key/)

Once you have the above define environment variables:

```bash
HOPSWORKS_HOST=REPLACE_WITH_YOUR_HOPSWOKRKS_CLUSTER_HOST
HOPSWORKS_API_KEY=REPLACE_WITH_YOUR_HOPSWORKS_API_KEY
HOPSWOERKS_PROJECT_NAME=REPLACE_WITH_YOUR_HOPSWOERKS_PROJECT_NAME
```

You will write real time feature data to feature group `taxi_ride` version `1`.
```bash
FEATURE_GROUP_NAME=taxi_ride
FEATURE_GROUP_VERSION=1
```

As we mentioned above your beam pipeline will read raw data from  publicly available `taxirides-realtime` topic 
```bash
SOURCE_TOPIC=projects/pubsub-public-data/topics/taxirides-realtime
```

Define required environment variables for your google cloud account:
```bash
# name of GCP service account
export SERVICE_ACCOUNT=REPLACE_WITH_YOUR__SERVICE_ACCOUNT_NAME
# GCP application credentials file
export GOOGLE_APPLICATION_CREDENTIALS=REPLACE_WITH_PATH_TO_YOUR_CREDENTIALS_FILE
# GCP bucket name for Dataflow to download temporary files
export BUCKET_NAME=REPLACE_WITH_YOUR_YOUR_BUCKET_NAME
# Google Cloud project ID to run the pipeline on. You can get this by: gcloud config get-value project
export PROJECT_NAME=REPLACE_WITH_YOUR_GOOGLE_PROJECT_ID 
# Dataflow regional endpoint
export REGION=REPLACE_WITH_NAME_OF_REGION
```

### Real time feature engineering in Beam/DataFlow
Beam is used for feature engineering when you need very fresh features computed in real-time. Beam/DataFlow pipelines
provide native support for aggregations, with dimensionality reduction algorithms and transformations.

Currently, Beam pipelines for Hopsworks Feature store are supported only in Java. Hopsworks Feature Store expects that 
your aggregation result is encapsulated in `org.apache.beam.sdk.values.Row` class and that it has the same schema as 
the feature group you are writing into. 

For example when you executed code in notebook `1_create_taxi_feature_group.ipynb` you created feature group
`taxi_ride` that has the following schema:

```
root
   |-- ride_id: string (nullable = true)
   |-- ride_status: string (nullable = true)
   |-- point_idx: integer (nullable = true)
   |-- longitude: double (nullable = true)
   |-- latitude: double (nullable = true)
   |-- meter_reading: double (nullable = true)
   |-- meter_increment: double (nullable = true)
   |-- passenger_count: integer (nullable = true)
```

This means that Hopsworks Feature store expects `org.apache.beam.sdk.values.Row` class with the following schema from 
Beam application to be able to write in `taxi_ride` feature group:

```java
Schema schema =
  Schema.of(
  Field.nullable("ride_id", FieldType.STRING),
  Field.nullable("ride_status", FieldType.STRING),
  Field.nullable("point_idx", FieldType.INT32),
  Field.nullable("longitude", FieldType.DOUBLE),
  Field.nullable("latitude", FieldType.DOUBLE),
  Field.nullable("meter_reading", FieldType.DOUBLE),
  Field.nullable("meter_increment", FieldType.DOUBLE),
  Field.nullable("passenger_count", FieldType.INT32)
  );
```

In the `com.hopsworks.tutorials.beam.TaxiRideInsertStream` you will find end to end code how to:
- read from source topic.
- convert to `org.apache.beam.sdk.values.Row` class with expected schema.
- get feature group handle and write real time features in to the online feature store.

To submit beam pipeline and write real time features to`taxi_ride` feature group execute the following command.

```bash
cd ./hopsworks-tutorials/java/beam
mvn compile exec:java \
  -Dexec.mainClass=com.hopsworks.tutorials.beam.TaxiRideInsertStream \
  -Dexec.cleanupDaemonThreads=false \
  -Dexec.args="\
    --hopsworksHost=$HOPSWORKS_HOST \
    --hopsworksApi=$HOPSWORKS_API_KEY \
    --hopsworksProject=$HOPSWOERKS_PROJECT_NAME \
    --featureGroupName=$FEATURE_GROUP_NAME \
    --featureGroupVersion=$FEATURE_GROUP_VERSION \
    --inputTopic=$SOURCE_TOPIC \
    --project=$PROJECT_NAME \
    --region=$REGION \
    --gcpTempLocation=gs://$BUCKET_NAME/temp \
    --runner=DataflowRunner"
```

#### Backfill feature data to offline FG
Above pipeline writes real time features to online feature store that stores the latest values per primary key(s). 
To save historical data for batch data analysis or model training you need to start backfill job. You can do this 
from Hopsworks jobs UI or CLI. 

To start Hopsworks job 1st make sure that you have Hopsworks Python library installed in your environment:
```bash
pip install hopsworks
```

Then execute the following command:
```bash
python3 ./backfill_job_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWOERKS_PROJECT_NAME --jobname taxi_ride_1_offline_fg_backfill
```

## Cleanup to avoid incurring charges to your GCP account for the resources created in this tutorial:
- `Ctrl+C` to stop the program in your terminal. Note that this does not actually stop the job if you use 
  `DataflowRunner`.
- Stop the Dataflow job in [GCP Console Dataflow page]. Cancel the job instead of draining it. This may take some 
  minutes.
- make sure to delete all VMs created by DataflowRunner (if any).
- Remove the Cloud Storage bucket.
```bash
gsutil rb gs://$BUCKET_NAME
```
