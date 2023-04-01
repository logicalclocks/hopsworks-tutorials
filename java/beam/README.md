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

   export GOOGLE_APPLICATION_CREDENTIALS=/Users/davitbzhalava/.config/gcloud/application_default_credentials.json
   export BUCKET_NAME=davit-eunorth-streaming
   export PROJECT_NAME=$(gcloud config get-value project)
   export REGION=europe-west1
   export SERVICE_ACCOUNT=hopsworks-ai@hops-20.iam.gserviceaccount.com

   gsutil mb gs://$BUCKET_NAME
   ```

## Setup

The following instructions will help you prepare your development environment.

1. Download and install the [Java Development Kit (JDK)].
   Verify that the [JAVA_HOME] environment variable is set and points to your JDK installation.

1. Download and install [Apache Maven] by following the [Maven installation guide] for your specific operating system.

1. Clone the `hopsworks-tutorials` repository.

    ```bash
    git clone https://github.com/logicalclocks/hopsworks-tutorials.git
    ```

1. Navigate to the sample code directory.

   ```bash
   cd hopsworks-tutorials/java/beam
   ```

## Streaming Analytics

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
mvn compile exec:java \
  -Dexec.mainClass=io.hops.examples.beam.TaxiRideInsertStream \
  -Dexec.cleanupDaemonThreads=false \
  -Dexec.args="\
    --hopsworksHost="3de2b490-ce4b-11ed-bafa-654da80d5ced.cloud.hopsworks.ai" \
    --hopsworksApi="pBKTZxnElPr71rnV.Z38La4X8J9ouAspRaFPodKsuwQVcgJUpxvjf3nCxlr4He90Gb1D7QXpw6VKGlwDS" \
    --hopsworksProject="pr_test" \
    --featureGroupName="taxi_ride" \
    --featureGroupVersion=7 \
    --inputTopic="projects/pubsub-public-data/topics/taxirides-realtime" \
    --project=$PROJECT_NAME \
    --region=$REGION \
    --gcpTempLocation=gs://$BUCKET_NAME/temp \
    --runner=DataflowRunner"
```


After the job has been submitted, you can check its status in the [GCP Console Dataflow page].
You can also check the output to your GCS bucket using the command line below or in the [GCP Console Storage page]. You may need to wait a few minutes for the files to appear.

```bash
gsutil ls gs://$BUCKET_NAME/samples/
```