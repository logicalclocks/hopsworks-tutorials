#!/bin/bash

# Predefine your Bucket Name
BUCKET_NAME='YOUR_BUCKET_NAME'


echo "spark.hadoop.hops.ipc.server.ssl.enabled=true" >> /etc/spark/conf/spark-defaults.conf
echo "spark.hadoop.fs.hopsfs.impl=io.hops.hopsfs.client.HopsFileSystem" >> /etc/spark/conf/spark-defaults.conf
echo "spark.hadoop.client.rpc.ssl.enabled.protocol=TLSv1.2" >> /etc/spark/conf/spark-defaults.conf
echo "spark.hadoop.hops.ssl.keystore.name=/etc/spark/conf/keyStore.jks" >> /etc/spark/conf/spark-defaults.conf
echo "spark.hadoop.hops.rpc.socket.factory.class.default=io.hops.hadoop.shaded.org.apache.hadoop.net.HopsSSLSocketFactory" >> /etc/spark/conf/spark-defaults.conf
echo "spark.hadoop.hops.ssl.keystores.passwd.name=/etc/spark/conf/material_passwd" >> /etc/spark/conf/spark-defaults.conf
echo "spark.sql.hive.metastore.jars=path" >> /etc/spark/conf/spark-defaults.conf
echo "spark.sql.hive.metastore.jars.path=gs://${BUCKET_NAME}/client/apache-hive-1.2.1-bin/lib/*,gs://${BUCKET_NAME}/client/hudi-spark3-bundle_2.12-0.10.0.3.jar,gs://${BUCKET_NAME}/hopsextra/hudi-utilities-bundle_2.12-0.10.0.3.jar" >> /etc/spark/conf/spark-defaults.conf
echo "spark.serializer=org.apache.spark.serializer.KryoSerializer" >> /etc/spark/conf/spark-defaults.conf
echo "spark.hadoop.hops.ssl.hostname.verifier=ALLOW_ALL" >> /etc/spark/conf/spark-defaults.conf
echo "spark.hadoop.hops.ssl.trustore.name=/etc/spark/conf/trustStore.jks" >> /etc/spark/conf/spark-defaults.conf

# Don't forget to specify your IP_ADDRESS and PORT!
echo "spark.hadoop.hive.metastore.uris thrift://{IP_ADDRESS}:{PORT}" >> /etc/spark/conf/spark-defaults.conf

gsutil cp gs://${BUCKET_NAME}/client/material_passwd.dms /etc/spark/conf/material_passwd
gsutil cp gs://${BUCKET_NAME}/client/keyStore.jks /etc/spark/conf/keyStore.jks
gsutil cp gs://${BUCKET_NAME}/client/trustStore.jks /etc/spark/conf/trustStore.jks


# Install custom library from GitHub
pip install "git+https://github.com/logicalclocks/hopsworks-api@main#egg=hopsworks&subdirectory=python"
pip install "git+https://github.com/logicalclocks/feature-store-api@master#egg=hsfs[python]&subdirectory=python"