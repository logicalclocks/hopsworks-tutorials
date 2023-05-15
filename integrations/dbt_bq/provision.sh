# Predefine a Cluster name, Region, and Project
CLUSTER_NAME='dbt-hops'
REGION='europe-central2'
PROJECT='hops-20'

# Cluster creation
gcloud dataproc clusters create $CLUSTER_NAME \
    --bucket maksym_gcs_bucket \
    --region $REGION \
    --zone europe-central2-c \
    --master-machine-type n1-standard-2 \
    --master-boot-disk-size 50GB \
    --num-workers 2 \
    --worker-machine-type n1-standard-2 \
    --worker-boot-disk-size 50GB \
    --image-version 2.0-debian10 \
    --optional-components JUPYTER \
    --project $PROJECT \
    --initialization-actions 'gs://goog-dataproc-initialization-actions-europe-central2/connectors/connectors.sh' \
    --metadata 'PIP_PACKAGES=hopsworks==3.2.0rc0' \
    --initialization-actions 'gs://maksym_gcs_bucket/pip-install.sh' \
    --metadata truststore-uri=gs://maksym_gcs_bucket/client/trustStore.jks \
    --properties=^#^spark:spark.jars=gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.23.2.jar,gs://maksym_gcs_bucket/client/hudi-spark3-bundle_2.12-0.10.0.3.jar,gs://maksym_gcs_bucket/client/hopsfs-client-3.2.0.5-EE-SNAPSHOT.jar,gs://maksym_gcs_bucket/client/hopsfs-client-api-3.2.0.5-EE-SNAPSHOT.jar,gs://maksym_gcs_bucket/client/hsfs-spark-3.2.0-RC0.jar,gs://maksym_gcs_bucket/client/spark-avro_2.12-3.1.1.3.jar,gs://maksym_gcs_bucket/client/spark-sql-kafka-0-10_2.12-3.1.1.3.jar,gs://maksym_gcs_bucket/client/hudi-utilities-bundle_2.12-0.10.0.3.jar
