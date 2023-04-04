# Example of Hopsworks Online Feature Store and Flink real time feature engineering pipeline 

#### Step 1:
```bash
git clone https://github.com/davitbzh/hopsworks-tutorials.git
cd ./hopsworks-tutorials/java
git checkout beam_flink
mvn clean package
```

#### Step 2:
On Hopsworks cluser execute 
- `setup/1_create_feature_groups.ipynb` to create feature groups
- `setup/2_create_topic_with_schema.ipynb` to create source kafka topic

```bash
HOPSWORKS_HOST=[HOPSWOKRKS_CLUSTER_HOST]
HOPSWORKS_API_KEY=[HOPSWORKS_API_KEY]
HOPSWOERKS_PROJECT_NAME=[HOPSWOERKS_PROJECT_NAME]
FEATURE_GROUP_NAME=[FEATURE_GROUP_NAME]
FEATURE_GROUP_VERSION=[FEATURE_GROUP_VERSION]
AGGREGATION_WINDOW_SIZE_MINUTES=[AGGREGATION_WINDOW_SIZE_MINUTES]
```

##### In this example we will use Credit card transaction simulator class SimProducer
#This is credit_card_transactions topic created in `setup/2_create_topic_with_schema.ipynb`
#Batch size controls how much events are simulated per second
```bash
SOURCE_TOPIC=credit_card_transactions
BATCH_SIZE=1
```

#### Step 3:
# to submit job from CLI you need to have latest hospworks installed on you conda env 
```bash
!pip install hopsworks
```

```bash
python3 ./flink/jobs_flink_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWOERKS_PROJECT_NAME --job transactionSource --jar ./flink/target/flink-3.2.0-SNAPSHOT.jar --main "com.hopsworks.tutorials.flink.fraud.SimProducer" --job_arguments "-topicName $SOURCE_TOPIC -batchSize $BATCH_SIZE"
```

#### Step 4:
```bash
python3 ./flink/jobs_flink_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWOERKS_PROJECT_NAME --job transactionConsumer --jar ./flink/target/flink-3.2.0-SNAPSHOT.jar --main "com.hopsworks.tutorials.flink.TransactionFraudExample" --job_arguments "-featureGroupName $FEATURE_GROUP_NAME -featureGroupVersion $FEATURE_GROUP_VERSION -sourceTopic $SOURCE_TOPIC -windowLength $AGGREGATION_WINDOW_SIZE_MINUTES"
```

#### Step 5: Go to hopsworks UI and start backfill job for offline FG
From Hopsworks jobs UI start backfill job "$FEATURE_GROUP_NAME_$FEATURE_GROUP_VERSION_offline_fg_backfill"
