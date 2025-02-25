# Online Feature Vector Retrieval Using Java Application

## Introduction
In this tutorial you will learn how to fetch feature vectors from online feature store for near real-time model serving
using external java application. 

## Clone tutorials repository
This section requires maven; java 1.8 and git.

```bash
git clone https://github.com/logicalclocks/hopsworks-tutorials
cd ./hopsworks-tutorials/java
mvn clean package
```

## Execute java application:
Now you will create [connection](https://docs.hopsworks.ai/hopsworks-api/3.3/generated/api/connection/) with
your Hopsworks cluster. For this you need to have Hopsworks cluster host address and [api key](https://docs.hopsworks.ai/3.3/user_guides/projects/api_key/create_api_key/)

Then define environment variables 

```bash
HOPSWORKS_HOST=f8d22ee0-e959-11ef-9eb9-1b4fa8c86bbb.cloud.hopsworks.ai
HOPSWORKS_API_KEY=O1NhbTQox8mClxyQ.x7chXShOxY0vKcVKQHJflRHDUk5aHxqZMSR1803LeUc5pPSFz4aJ8dFPTBOw8QQn
HOPSWORKS_PROJECT_NAME=aaa

FEATURE_GROUP_NAME=java_data
FEATURE_GROUP_VERSION=1
FEATURE_VIEW_NAME=products_fv
FEATURE_VIEW_VERSION=1
```

```bash
python3 ./setup_fv_fg.py --host $HOPSWORKS_HOST --api_key $HOPSWORKS_API_KEY --project $HOPSWORKS_PROJECT_NAME  --feature_group_name $FEATURE_GROUP_NAME --feature_group_version $FEATURE_GROUP_VERSION  --feature_view_name $FEATURE_VIEW_NAME --feature_view_version $FEATURE_VIEW_VERSION
java -jar ./target/hopsworks-java-tutorial-3.9.0-RC12-jar-with-dependencies.jar $HOPSWORKS_HOST $HOPSWORKS_API_KEY $HOPSWORKS_PROJECT_NAME $FEATURE_GROUP_NAME $FEATURE_GROUP_VERSION $FEATURE_VIEW_NAME $FEATURE_VIEW_VERSION
```
