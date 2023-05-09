# Predefine variables
CLUSTER_NAME='YOUR_CLUSTER_NAME'
REGION='YOUR_REGION'
ZONE='YOUR_ZONE'
PROJECT='YOUR_PROJECT_NAME'
BUCKET='YOUR_BUCKET_NAME'

# Dataproc cluster creation
gcloud dataproc clusters create $CLUSTER_NAME \
    --bucket $BUCKET \
    --region $REGION \
    --zone $ZONE \
    --project $PROJECT \
    --master-machine-type n1-standard-2 \
    --master-boot-disk-size 50GB \
    --num-workers 2 \
    --worker-machine-type n1-standard-2 \
    --worker-boot-disk-size 50GB \
    --image-version 2.0-debian10 \
    --optional-components JUPYTER \
    --initialization-actions 'gs://goog-dataproc-initialization-actions-${REGION}/connectors/connectors.sh' \
    --initialization-actions 'gs://goog-dataproc-initialization-actions-${REGION}/python/pip-install.sh' \
    --metadata bigquery-connector-version=1.2.0 \
    --metadata spark-bigquery-connector-version=0.21.0 \
    --metadata 'PIP_PACKAGES=hopsworks==3.1.0rc0' \
    --properties spark:spark.jars=gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.23.2.jar
