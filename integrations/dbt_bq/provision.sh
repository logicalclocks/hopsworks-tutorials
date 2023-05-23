# Predefine variables
CLUSTER_NAME='YOUR_CLUSTER_NAME'
REGION='YOUR_REGION'
PROJECT='YOUR_PROJECT_NAME'
BUCKET_NAME='YOUR_BUCKET_NAME'

# Cluster creation
gcloud dataproc clusters create $CLUSTER_NAME \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --zone europe-central2-c \
    --master-machine-type n1-standard-2 \
    --master-boot-disk-size 50GB \
    --num-workers 2 \
    --worker-machine-type n1-standard-2 \
    --worker-boot-disk-size 50GB \
    --image-version 2.0-debian10 \
    --project $PROJECT \
    --initialization-actions 'gs://goog-dataproc-initialization-actions-europe-central2/connectors/connectors.sh' \
    --initialization-actions=gs://$BUCKET_NAME/configureSpark.sh \
    --properties=^#^spark:spark.jars=gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.23.2.jar,gs://$BUCKET_NAME/client/hopsfs-client-3.2.0.5-EE-SNAPSHOT.jar,gs://$BUCKET_NAME/client/hopsfs-client-api-3.2.0.5-EE-SNAPSHOT.jar,gs://$BUCKET_NAME/client/hudi-spark3-bundle_2.12-0.10.0.3.jar,gs://$BUCKET_NAME/client/hsfs-spark-3.3.0-RC0.jar#spark:spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.3,org.apache.spark:spark-avro_2.12:3.1.3