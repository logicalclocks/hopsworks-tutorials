<!--
[![hopsworks-tutorials](https://github.com/logicalclocks/hopsworks-tutorials/actions/workflows/test-python-37.yml/badge.svg)](https://github.com/logicalclocks/hopsworks-tutorials/actions/workflows/test-python-37.yml)

[![hopsworks-tutorials](https://github.com/logicalclocks/hopsworks-tutorials/actions/workflows/test-python-38.yml/badge.svg)](https://github.com/logicalclocks/hopsworks-tutorials/actions/workflows/test-python-38.yml)

[![hopsworks-tutorials](https://github.com/logicalclocks/hopsworks-tutorials/actions/workflows/test-python-39.yml/badge.svg)](https://github.com/logicalclocks/hopsworks-tutorials/actions/workflows/test-python-39.yml)
-->

# 👨🏻‍🏫 Hopsworks Tutorials
We are happy to welcome you to our collection of tutorials dedicated to exploring the fundamentals of Hopsworks and Machine Learning development. In addition to offering different types of use cases and common subjects in the field, it facilitates navigation and use of models in a production environment using Hopsworks Feature Store.

## ⚙️ How to run the tutorials:
For the tutorials to work, you will need a Hopsworks account. To do so, go to app.hopsworks.ai and create one. With a managed account, just run the Jupyter notebook from within Hopsworks.

Generally the notebooks contain the information you will need on how to interact with the Hopsworks Platform.

If you have an [app.hopsworks.ai](https://app.hopsworks.ai) account; you may connect to Hopsworks with the following line; this will prompt you with a link to your Token which will link to the feature store. 

```python
import hopsworks
 
project = hopsworks.login()
fs = project.get_feature_store()
```

In some cases, you may also need to install Hopsworks; to be able to work with the package. Simply start your notebook with: 
```python
!pip install -U hopsworks --quiet
```
The walkthrough and tutorials are provided in the form of Python notebooks, you will therefore need to run a jupyter environment or work within a colaboratory notebook in google; the later option might lead to some minor errors being displayed or libraries might require different library versions to work.

## ✍🏻 Concepts:
In order to understand the tutorials you need to be familiar with general concepts of Machine Learning and Python development. You may find some useful information in the [Hopsworks documentation.](https://docs.hopsworks.ai) 

## 🗄️ Table of Content:

- Basic Tutorials:
    - [QuickStart](https://github.com/logicalclocks/hopsworks-tutorials/blob/master/quickstart.ipynb): Introductory tutorial to get started quickly.
    - [Churn](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/churn): Predict customers that are at risk of churning.
    - [Fraud Batch](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/fraud_batch): Detect Fraud Transactions (Batch use case).
    - [Fraud Online](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/fraud_online): Detect Fraud Transactions (Online use case).
    - [Iris](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/iris): Classify iris flower species.
    - [Loan Approval](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/loan_approval): Predict loan approvals.
- Advanced Tutorials:
    - [Air Quality](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/air_quality): Predict the Air Quality value (PM2.5) in Europe and USA using weather features and air quality features of the previous days.
    - [Bitcoin](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/bitcoin): Predict Bitcoin price using timeseries features and tweets sentiment analysis.
    - [Citibike](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/citibike): Predict the number of citibike users on each citibike station in the New York City.
    - [Credit Scores](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/credit_scores): Predict clients' repayment abilities.
    - [Electricity](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/electricity): Predict the electricity prices in several Swedish cities based on weather conditions, previous prices, and Swedish holidays.
    - [NYC Taxi Fares](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/nyc_taxi_fares): Predict the fare amount for a taxi ride in New York City given the pickup and dropoff locations.
    - [Recommender System](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/recommender-system): Build a recommender system for fashion items.
    - [TimeSeries](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/timeseries): Timeseries price prediction.
    - [Keras model and Sklearn Transformation Functions with Hopsworks Model Registry](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/transformation_functions/keras): How to register Sklearn Transformation Functions and Keras model in the Hopsworks Model Registry, how to retrieve them and then use in training and inference pipelines.
    - [PyTorch model and Sklearn Transformation Functions with Hopsworks Model Registry](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/transformation_functions/pytorch): How to register Sklearn Transformation Functions and PyTorch model in the Hopsworks Model Registry, how to retrieve them and then use in training and inference pipelines.
    - [Sklearn Transformation Functions With Hopsworks Model Registy](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/transformation_functions/sklearn): How to register sklearn.pipeline with transformation functions and classifier in Hopsworks Model Registry and use it in training and inference pipelines.
    - [Custom Transformation Functions](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/transformation_functions/custom): How to register custom transformation functions in hopsworks feature store use then in training and inference pipelines.
- Integrations: 
    - [BigQuery Storage Connector](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/big_query): Create an External Feature Group using BigQuery Storage Connector.
    - [Google Cloud Storage](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/gcs): Create an External Feature Group using GCS Storage Connector.
    - [Redshift](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/redshift): Create an External Feature Group using Redshift Storage Connector.
    - [Snowflake](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/snowflake): Create an External Feature Group using Snowflake Storage Connector.
    - [DBT Tutorial with BigQuery](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/dbt_bq): Perform feature engineering in DBT on BigQuery.
    - [WandB](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/wandb): Build a machine learning model with Weights & Biases.
    - [Great Expectations](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/great_expectations): Introduction to Great Expectations concepts and classes which are relevant for integration with the Hopsworks MLOps platform.
    - [Neo4j](integrations/neo4j): Perform Anti-money laundering (AML) predictions using Neo4j Graph representation of transactions.
    - [Polars](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/advanced_tutorials/polars/quickstart.ipynb) : Introductory tutorial on using Polars.
    - [Monitoring](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/monitoring): How to implement feature monitoring in your production pipeline.
    - [Bytewax](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/bytewax): Real time feature computation using Bytewax.
    - [Apache Beam](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/java/beam): Real time feature computation using Apache Beam, Google Cloud Dataflow and Hopsworks Feature Store.
    - [Apache Flink](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/java/flink): Real time feature computation using Apache Flink and Hopsworks Feature Store.
    - [MageAI](https://github.com/logicalclocks/hopsworks-tutorials/tree/master/integrations/mage_ai): Build and operate a ML system with Mage and Hopsworks.
   

## 📝 Feedbacks & Comments:
We welcome feedbacks and suggestions, you can contact us on any of the following channels:
- Our [Support Forum](https://community.hopsworks.ai/),
- Directly on this [github repository](https://github.com/logicalclocks/hopsworks-tutorials),
- Send us an email at info@hopsworks.ai 
