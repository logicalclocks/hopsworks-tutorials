# Real time feature computation using Apache Flink.

## Introduction
In this guide you will learn how to create a real-time feature engineering pipeline and write real-time features 
and build TikTok stile recommender system using Hopsworks features store. 

## Clone tutorials repository
```bash
git clone https://github.com/logicalclocks/hopsworks-tutorials
cd ~/hopsworks-tutorials/advanced_tutorials/tiktok-recsys
```

## Install required python libraries
For the tutorials to work, you need to Install the required python libraries 
```bash
cd ./python
pip install -r requirements.txt
```

Once you have the above, define the following environment variable:

## Define env variables
```bash
export HOPSWORKS_HOST=REPLACE_WITH_YOUR_HOPSWORKS_CLUSTER_HOST
export HOPSWORKS_PROJECT_NAME=REPLACE_WITH_YOUR_HOPSWORKS_PROJECT_NAME
export HOPSWORKS_API_KEY=REPLACE_WITH_YOUR_HOPSWORKS_API_KEY
export MAX_ID_RANGE=100
export RECORDS_PER_SECOND=10
export PARALLELISM=1
```

## Create a Feature Groups
Full documentation how to create feature group using HSFS APIs can be found [here](https://docs.hopsworks.ai/latest/user_guides/fs/feature_group/create/).

```bash
python ./setup/tiktok_interactions_feature_groups.py
python ./setup/tiktok_user_window_agg_feature_group.py
python ./setup/tiktok_video_window_agg_feature_group.py
```

## Flink pipeline:
```bash
cd ~/hopsworks-tutorials/advanced_tutorials/tiktok-recsys/java
mvn clean package
```
### Submit Flink job
```bash
python3 ./jobs_flink_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWORKS_PROJECT_NAME --job tikTokInteractions --jar ./target/flink-tiktok-0.1.0.jar --main "ai.hopsworks.tutorials.flink.tiktok.TikTokFlink" --job_arguments "-maxIdRange $MAX_ID_RANGE -recordsPerSecond $RECORDS_PER_SECOND -parallelism $PARALLELISM"
```

