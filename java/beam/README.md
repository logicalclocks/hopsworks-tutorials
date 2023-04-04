# Stream Cloud Pub/Sub with Cloud Dataflow and Hopsworks

Sample(s) showing how to use [Google Cloud Pub/Sub] with [Google Cloud Dataflow].

## Before you begin

1. Install the [Cloud SDK].

1. Setup the Cloud SDK to your GCP project.

   ```bash
   gcloud init
   ```

1. [Create a service account key] as a JSON file.
   For more information, see [Creating and managing service accounts].

    * From the **Service account** list, select **New service account**.
    * In the **Service account name** field, enter a name.
    * From the **Role** list, select **Project > Owner**.

      > **Note**: The **Role** field authorizes your service account to access resources.
      > You can view and change this field later by using the [GCP Console IAM page].
      > If you are developing a production app, specify more granular permissions than **Project > Owner**.
      > For more information, see [Granting roles to service accounts].

    * Click **Create**. A JSON file that contains your key downloads to your computer.

1. Set your `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account key file. and 
   Create a Cloud Storage bucket.

   ```bash   
   export JAVA_HOME=`/usr/libexec/java_home -v 1.8`
   export PATH=$PATH:$JAVA_HOME/Contents/Commands

   export GOOGLE_APPLICATION_CREDENTIALS=[PATH_TO_YOUR_CREDENTIALS_FILE]
   export BUCKET_NAME=[NAME_OF_YOUR_BUCKET]
   export PROJECT_NAME=$(gcloud config get-value project)
   export REGION=[NAME_OF_REGION]
   export SERVICE_ACCOUNT=[NAME_OF_SERVICE_ACCOUNT]
   
   gsutil mb gs://$BUCKET_NAME
   ```

## Setup

The following instructions will help you prepare your development environment.

1. Download and install the [Java Development Kit (JDK)].
   Verify that the [JAVA_HOME] environment variable is set and points to your JDK installation.

1. Download and install [Apache Maven] by following the [Maven installation guide] for your specific operating system.

1. Clone the `hopsworks-tutorials` repository.

    ```bash
    git clone https://github.com/davitbzh/hopsworks-tutorials.git
    cd ./hopsworks-tutorials/java/beam
    git checkout beam_flink
    ```

## Streaming Analytics
On Hopsworks cluser execute
- `setup/1_create_taxi_feature_group.ipynb` to create feature groups

### Google Cloud Pub/Sub to Google Cloud Storage
The following example will run a streaming pipeline. It will read messages from a Pub/Sub topic, Hopsworks Feature store

+ `--hopsworksHost`: sets Hopsworks cluster host
+ `--hopsworksApi`: sets API key to authenticate with Hopsworks
+ `--hopsworksProject`: sets Name of the Hopsworks project to connect to
+ `--featureGroupName`: sets Name of the Feature group to write to
+ `--featureGroupVersion`: sets Version of the Feature group to write to
+ `--inputTopic`: sets the input Pub/Sub topic to read messages from
+ `--project`: sets the Google Cloud project ID to run the pipeline on
+ `--region`: sets the Dataflow regional endpoint
+ `--gcpTempLocation`: sets a GCP location for Dataflow to download temporary files
+ `--runner [optional]`: specifies the runner to run the pipeline, defaults to `DirectRunner`


```bash
HOPSWORKS_HOST=[HOPSWOKRKS_CLUSTER_HOST]
HOPSWORKS_API_KEY=[HOPSWORKS_API_KEY]
HOPSWOERKS_PROJECT_NAME=[HOPSWOERKS_PROJECT_NAME]
FEATURE_GROUP_NAME=[FEATURE_GROUP_NAME]
FEATURE_GROUP_VERSION=[FEATURE_GROUP_VERSION]

# this is publicly available google topic you can subscribe to
SOURCE_TOPIC=projects/pubsub-public-data/topics/taxirides-realtime

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

#### Start backfill job for offline FG
From Hopsworks jobs UI start backfill job "$FEATURE_GROUP_NAME_$FEATURE_GROUP_VERSION_offline_fg_backfill"

## Cleanup

1. `Ctrl+C` to stop the program in your terminal. Note that this does not actually stop the job if you use `DataflowRunner`. Skip 3 if you use the `DirectRunner`.

1. Stop the Dataflow job in [GCP Console Dataflow page]. Cancel the job instead of draining it. This may take some minutes.

1. To avoid incurring charges to your GCP account make sure to delete all VMs created by DataflowRunner.

1. To avoid incurring charges to your GCP account for the resources created in this tutorial:

    ```bash
    # Delete only the files created by this sample.
    gsutil -m rm -rf "gs://$BUCKET_NAME/output*"
    gsutil -m rm -rf "gs://$BUCKET_NAME/samples/output*"
    gsutil -m rm -rf "gs://$BUCKET_NAME/samples"
    gsutil -m rm -rf "gs://$BUCKET_NAME/temp/*"
    gsutil -m rm -rf "gs://$BUCKET_NAME/temp"
    
    # [optional] Remove the Cloud Storage bucket.
    gsutil rb gs://$BUCKET_NAME
    ```
