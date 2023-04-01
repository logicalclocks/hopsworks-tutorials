# Example of Hopsworks Online Feature Store and Flink real time feature engineering pipeline 

#### Step 1:
```bash
git clone https://github.com/davitbzh/loadtest.git
cd ./loadtest/tests/java/flink
git checkout java_tests
mvn clean package
```

#### Step 2:
On Hopsworks cluser execute 
- `setup/1_create_feature_groups.ipynb` to create feature groups
- `setup/2_create_topic_with_schema.ipynb` to create source kafka topic

## Option 1
#### Step 3:
From Hopsworks jobs UI start
- producer job and from Flink jobs UI upload jar file  `target/hops-examples-flink-3.1.0-SNAPSHOT.jar` 
- submit job with class path `io.hops.examples.flink.fraud.SimProducer` with arguments `-topicName credit_card_transactions -batchSize 1`

#### Step 4:
From Hopsworks jobs UI start
- consumer job and from Flink jobs UI upload jar file  `target/hops-examples-flink-3.1.0-SNAPSHOT.jar`
- submit job with class path `io.hops.examples.flink.examples.TransactionFraudExample` with arguments `-featureGroupName card_transactions_10m_agg -featureGroupVersion 1 -sourceTopic credit_card_transactions -windowLength 10 -featureNameWindowLength 10m`

#### Step 5:
From Hopsworks jobs UI start backfill job `card_transactions_10m_agg_1_offline_fg_backfill`

## Option 2
python3 ./jobs_flink_client.py --host 6614ea70-98b6-11ed-a28a-a1e10e28daf5.cloud.hopsworks.ai \
--api_key "pBKTZxnElPr71rnV.Z38La4X8J9ouAspRaFPodKsuwQVcgJUpxvjf3nCxlr4He90Gb1D7QXpw6VKGlwDS" \
--project "pr_test" --jar ./flink/target/flink-3.2.0-SNAPSHOT.jar --main "io.hops.examples.flink.fraud.SimProducer" \ 
--job_arguments "-topicName credit_card_transactions -batchSize 1"

python3 ./jobs_flink_client.py --host 6614ea70-98b6-11ed-a28a-a1e10e28daf5.cloud.hopsworks.ai \
--api_key "pBKTZxnElPr71rnV.Z38La4X8J9ouAspRaFPodKsuwQVcgJUpxvjf3nCxlr4He90Gb1D7QXpw6VKGlwDS" \ 
--project "pr_test" --jar ./flink/target/flink-3.2.0-SNAPSHOT.jar \ 
--main "io.hops.examples.flink.examples.TransactionFraudExample" \ 
--job_arguments "-topicName credit_card_transactions -batchSize 1"

