# Real time feature computation using Apache Flink and Hopsworks Feature Store

## Introduction
In this guide you will learn how to create Real-Time Feature Engineering pipeline and write real time features in to 
the Hopsworks features store. This guide covers

- computing real time features with Apache Flink. 
- writing real time features into the Hopsworks's online feature store using `hsfs-flink` library. 

You will also 
- create feature group using the HSFS APIs.
- Backfill feature data to offline feature group.

## Before you begin
For the tutorials to work, you need [managed.hopsworks.ai](https://managed.hopsworks.ai) account or on premise 
Hopsworks deployment. Note that this tutorial will not work for [app.hopsworks.ai](https://app.hopsworks.ai) account 
as submitting custom jobs to [app.hopsworks.ai](https://app.hopsworks.ai) are not supported. 

You can find documentation how to get started on [GCP](https://docs.hopsworks.ai/3.1/setup_installation/gcp/getting_started/),
[AWS](https://docs.hopsworks.ai/3.1/setup_installation/aws/getting_started/) or on [Azure](https://docs.hopsworks.ai/3.1/setup_installation/azure/getting_started/).

You also need to have configured maven; java 1.8 and git.

## Clone tutorials repository
```bash
git clone https://github.com/logicalclocks/hopsworks-tutorials
cd ./hopsworks-tutorials/integrations/java
mvn clean package
```

## Create Feature Groups
Currently, Flink support for Hopsworks feature store is experimental and only write operation is supported. This means 
that Feature group metadata needs to be registered in Hopsworks Feature store before you can write real time features computed 
by Flink.

Full documentation how to create feature group using the HSFS APIs can be found [here](https://docs.hopsworks.ai/3.1/user_guides/fs/feature_group/create/).

This tutorial comes with notebook with a code to create feature groups:
- `. /hopsworks-tutorials/java/flink/setup/1_create_feature_groups.ipynb`

You can execute this notebook directly on Hopsworks cluster. Follow the documentation how to run [spark notebooks](https://docs.hopsworks.ai/3.1/user_guides/projects/jupyter/spark_notebook/)
and [python notebooks](https://docs.hopsworks.ai/3.1/user_guides/projects/jupyter/python_notebook/).

## Create Kafka topic for data source
Feature pipeline needs to connect to some data source to read the data to be processed. In this tutorial you will 
simulate card transaction and write to kafka topic that will be used as a source for Flink's real time feature engineering pipeline.

Here is the notebook with code that sets up kafka topic on your Hopsworks cluster
- `./hopsworks-tutorials/java/flink/setup/2_create_topic_with_schema.ipynb` to create source kafka topic

## Submit Flink Jobs:
In this tutorial you will submit Flink job using combination of the [Hopsworks job's](https://docs.hopsworks.ai/hopsworks-api/3.1/generated/api/jobs/) and 
the [Flink](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/ops/rest_api/) REST APIs. You need to have Hopsworks Python library installed in your environment:

```bash
pip install hopsworks
```

Next you need to create [connection](https://docs.hopsworks.ai/hopsworks-api/3.1/generated/api/connection/) with 
your Hopsworks cluster. For this you need to have Hopsworks cluster host address and [api key](https://docs.hopsworks.ai/3.1/user_guides/projects/api_key/create_api_key/)

Once you have the above define environment variables: 

```bash
HOPSWORKS_HOST=REPLACE_WITH_YOUR_HOPSWOKRKS_CLUSTER_HOST
HOPSWORKS_API_KEY=REPLACE_WITH_YOUR_HOPSWORKS_API_KEY
HOPSWOERKS_PROJECT_NAME=REPLACE_WITH_YOUR_HOPSWOERKS_PROJECT_NAME
```

### Simulate card transactions and write to source topic
Run the following command to produce raw card transactions and sync to topic `credit_card_transactions` that will be 
used as a source for real time feature engineering pipeline: 

```bash
python3 ./flink/jobs_flink_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWOERKS_PROJECT_NAME --job transactionSource --jar ./flink/target/flink-3.3.0-SNAPSHOT.jar --main "com.hopsworks.tutorials.flink.fraud.SimProducer" --job_arguments "-topicName credit_card_transactions -batchSize 1"
```

### Real time feature engineering in Flink
Flink is used for feature engineering when you need very fresh features computed in real-time. Flink pipelines 
provide native support for aggregations, with dimensionality reduction algorithms and transformations.

Currently, Flink pipelines for Hopsworks Feature store are supported in Java only. Hopsworks Feature Store expects that 
your aggregation result is encapsulated in POJO class and that has the same schema as the feature group 
you are writing into. In database terms this POJO class corresponds to one row.

For example when you executed code in notebook `1_create_feature_groups.ipynb` you created feature group 
`card_transactions_10m_agg` that has the following schema: 

```
root
    |-- cc_num: long (nullable = true)
    |-- num_trans_per_10m: long (nullable = true)
    |-- avg_amt_per_10m: double (nullable = true)
    |-- stdev_amt_per_10m: double (nullable = true)
```

This means that Hopsworks Feature store expects following POJO class from Flink application to be able to write in `card_transactions_10m_agg`
feature group:

```java
public class TransactionTenMinAgg {
  Long cc_num;
  Long num_trans_per_10m;
  Double avg_amt_per_10m;
  Double stdev_amt_per_10m;

  public Long getCcNum() {
    return cc_num;
  }
  public void setCcNum(Long value) {
    this.cc_num = value;
  }
  public Long getNumTransPer10m() {
    return num_trans_per_10m;
  }
  public void setNumTransPer10m(Long value) {
    this.num_trans_per_10m = value;
  }
  public Double getAvgAmtPer10m() {
    return avg_amt_per_10m;
  }
  public void setAvgAmtPer10m(Double value) {
    this.avg_amt_per_10m = value;
  }
  public Double getStdevAmtPer10m() {
    return stdev_amt_per_10m;
  }
  public void setStdevAmtPer10m(Double value) {
    this.stdev_amt_per_10m = value;
  }
}
```

In the `com.hopsworks.tutorials.flink.TransactionFraudExample` you will find end to end code how to:
- read from source topic.
- perform time window based aggregation.
- get feature group handle and write real time features computed by flink in to the online feature store.  

To submit flink pipeline that computes aggregates on 10 minute window and writes to `card_transactions_10m_agg`
feature group execute the following command.

```bash
python3 ./flink/jobs_flink_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWOERKS_PROJECT_NAME --job transactionConsumer --jar ./flink/target/flink-3.3.0-SNAPSHOT.jar --main "com.hopsworks.tutorials.flink.TransactionFraudExample" --job_arguments "-featureGroupName card_transactions_10m_agg -featureGroupVersion 1 -sourceTopic credit_card_transactions -windowLength 10"
```

#### Backfill feature data to offline feature group
Above pipeline writes real time features to online feature store which stores the latest values per 
primary key(s). To save historical data for batch data analysis or model training you need to start backfill job.
You can do this from Hopsworks jobs UI or run the following command: 

```bash
python3 ./flink/backfill_job_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWOERKS_PROJECT_NAME --jobname card_transactions_10m_agg_1_offline_fg_backfill
```
