# Real time feature computation using Bytewax.

## Introduction
In this guide you will learn how to create a real-time feature engineering pipeline and write real-time features in to
the Hopsworks features store. This guide covers:

- computing real-time features from a streaming data source (WebSockets) with Bytewax.
- writing real-time features to Hopsworks's online feature group via the streaming platform, Kafka.

You will also
- create feature group using the HSFS APIs.
- Backfill feature data to offline feature group.

## Before you begin
For the tutorials to work, you need:
- Hopsworks account
[managed.hopsworks.ai](https://managed.hopsworks.ai) account or on premise Hopsworks deployment. Note that this tutorial 
will not work for [app.hopsworks.ai](https://app.hopsworks.ai) account as submitting custom jobs to 
[app.hopsworks.ai](https://app.hopsworks.ai) are not supported.

You can find documentation on how to get started on [GCP](https://docs.hopsworks.ai/3.1/setup_installation/gcp/getting_started/),
[AWS](https://docs.hopsworks.ai/3.1/setup_installation/aws/getting_started/) or on [Azure](https://docs.hopsworks.ai/3.1/setup_installation/azure/getting_started/).

Install required python libraries 
```bash
pip install hopsworks
pip install bytewax
pip install websocket-client
```

you also need  to have Hopsworks cluster host address, hopsworks project name and 
[api key](https://docs.hopsworks.ai/3.1/user_guides/projects/api_key/create_api_key/)

Once you have the above define environment variables:

```bash
export HOPSWORKS_HOST=REPLACE_WITH_YOUR_HOPSWOKRKS_CLUSTER_HOST
export HOPSWORKS_API_KEY=REPLACE_WITH_YOUR_HOPSWORKS_API_KEY
export HOPSWOERKS_PROJECT_NAME=REPLACE_WITH_YOUR_HOPSWOERKS_PROJECT_NAME
```

## Clone tutorials repository
```bash
git clone https://github.com/logicalclocks/hopsworks-tutorials
cd ./hopsworks-tutorials/integrations/bytewax
```

## Create Feature Groups
Currently, bytewax support for Hopsworks feature store is experimental and only write operation is supported. This means
that Feature group metadata needs to be registered in Hopsworks Feature store before you can write real time features computed
by Bytewax.

Full documentation how to create feature group using HSFS APIs can be found [here](https://docs.hopsworks.ai/3.1/user_guides/fs/feature_group/create/).

This tutorial comes with a python program to create a feature group:
- `python ./setup/feature_group.py`


## Data source
Feature pipeline needs to connect to some data source to read the data to be processed. In this tutorial you will
subscribe to publicly available Coinbase websocket. 

## Start Bytewax pipeline:
Now you are ready to run a streaming pipeline using Bytewax and write real time feature data to feature group 
`order_book` version `1`.

```bash
FEATURE_GROUP_NAME=order_book
FEATURE_GROUP_VERSION=1
```

### Real time feature engineering in Bytewax
To submit Bytewax pipeline and write real time features to`order_book` feature group execute the following command.

```bash
python -m bytewax.run "orderbook:get_flow('$FEATURE_GROUP_NAME', $FEATURE_GROUP_VERSION)" 
```

#### Materialize feature data to offline FG
Above pipeline writes real time features to online feature store that stores the latest values per primary key(s). 
To save historical data for batch data analysis or model training you need to start offline feature group 
materialization job. 

```bash
python3 ./materialization_job_client.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWOERKS_PROJECT_NAME --jobname ${FEATURE_GROUP_NAME}_${FEATURE_GROUP_VERSION}_offline_fg_materialization
```