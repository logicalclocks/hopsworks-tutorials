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
your Hopsworks cluster. For this you need to have Hopsworks cluster host address and [api key](https://docs.hopsworks.ai/latest/user_guides/projects/api_key/create_api_key/)

Then define environment variables 

```bash
HOPSWORKS_HOST=REPLACE_WITH_YOUR_HOPSWORKS_CLUSTER_HOST
HOPSWORKS_API_KEY=REPLACE_WITH_YOUR_HOPSWORKS_API_KEY
HOPSWORKS_PROJECT_NAME=REPLACE_WITH_YOUR_HOPSWORKS_PROJECT_NAME
```

```bash
java -jar ./target/hopsworks-java-tutorial-3.9.0-RC9-jar-with-dependencies.jar $HOPSWORKS_HOST $HOPSWORKS_API_KEY $HOPSWORKS_PROJECT_NAME
```
