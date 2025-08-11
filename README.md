# 👨🏻‍🏫 Hopsworks Tutorials

We are happy to welcome you to our collection of tutorials dedicated to exploring the fundamentals of Hopsworks and Machine Learning development. In addition to offering different types of use cases and common subjects in the field, it facilitates navigation and use of models in a production environment using Hopsworks Feature Store.

## ⚙️ How to run the tutorials:
For the tutorials to work, you will need a Hopsworks account. To do so, go to app.hopsworks.ai and create one. With a managed account, just run the Jupyter notebook from within Hopsworks.

If you have an [app.hopsworks.ai](https://app.hopsworks.ai) account; you may connect to Hopsworks with the following line; this will prompt you with a link to your Token which will link to the feature store. 

```python
import hopsworks
 
project = hopsworks.login()
fs = project.get_feature_store()
```

In some cases, you may also need to install Hopsworks; to be able to work with the package. Simply start your notebook with: 
```python
!pip install -U 'hopsworks[python]' --quiet
```

## ✍🏻 Concepts:
Familiarity with Machine Learning and Python development is recommended. For more information, visit the [Hopsworks documentation.](https://docs.hopsworks.ai)

## 🗄️ Table of Content:

- [QuickStart](https://github.com/logicalclocks/hopsworks-tutorials/blob/branch-4.5/quickstart.ipynb): Introductory tutorial to get started quickly.

### 🚀 Real-time AI Systems
- [Fraud Online](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/real-time-ai-systems/fraud_online): Detect Fraud Transactions
- [AML](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/real-time-ai-systems/aml): Anti-money laundering predictions
- [TikTok RecSys](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/real-time-ai-systems/tiktok_recsys): TikTok-style recommendation system
- [TimeSeries](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/real-time-ai-systems/timeseries): Timeseries price prediction

### ⚙️ Batch AI Systems
- [Loan Approval](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/batch-ai-systems/loan_approval): Predict loan approvals
- [Fraud Batch](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/batch-ai-systems/fraud_batch): Detect Fraud Transactions
- [Churn](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/batch-ai-systems/churn): Predict customers at risk of churning
- [Credit Scores](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/batch-ai-systems/credit_scores): Predict clients' repayment abilities
- [Hospital Wait Time](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/batch-ai-systems/hospital_wait_time): Predict waiting time for deceased donor kidneys
- [NYC Taxi Fares](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/batch-ai-systems/nyc_taxi_fares): Predict NYC taxi fare amounts

### 🔮 LLM AI Systems
- [Fraud Cheque Detection](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/llm-ai-systems/fraud_cheque_detection): AI assistant for detecting fraudulent scanned cheques
- [LLM PDF](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/llm-ai-systems/llm_pdfs): RAG-based AI assistant for PDF document Q&A
- [Recommender System](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/llm-ai-systems/recommender-system): Fashion items recommender system

### 🧬 API Examples
- Vector Similarity Search:
  - [Feature Group Embeddings API](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/vector_similarity_search/1_feature_group_embeddings_api.ipynb)
  - [Feature View Embeddings API](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/vector_similarity_search/2_feature_view_embeddings_api.ipynb)
- [Datasets](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/datasets.ipynb)
- [Feature Group Change Notification CDC](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/feature_group_change_notification_cdc.ipynb)
- [Feature Monitoring](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/feature_monitoring.ipynb)
- [Git Integration](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/git.ipynb)
- [Jobs Management](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/jobs.ipynb)
- [Kafka Integration](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/kafka.ipynb)
- [OpenSearch Integration](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/opensearch.ipynb)
- [Projects Management](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/projects.ipynb)
- [Secrets Management](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/api_examples/secrets.ipynb)

### 🔬 Integrations
- [Airflow GCP](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/airflow_gcp): Apache Airflow integration with Google Cloud Platform.
- [AzureSQL](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/azuresql): Create an External Feature Group using Azure SQL Database.
- [BigQuery](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/big_query): Create an External Feature Group using BigQuery Storage Connector.
- [Bytewax](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/bytewax): Real-time feature computation using Bytewax.
- [DBT with BigQuery](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/dbt_bq): Perform feature engineering in DBT on BigQuery.
- [Federated Offline Query](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/federated-offline-query): Execute federated queries across offline data sources.
- [Google Cloud Storage](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/gcs): Create an External Feature Group using GCS Storage Connector.
- [Great Expectations](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/great_expectations): Introduction to Great Expectations concepts for Hopsworks MLOps platform.
- [Java](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/java): Java-based integrations including Apache Beam and Apache Flink.
- [LangChain](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/langchain): Integration with LangChain for LLM applications.
- [MageAI](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/mage_ai): Build and operate ML systems with Mage and Hopsworks.
- [Neo4j](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/neo4j): Perform Anti-money laundering predictions using Neo4j Graph.
- [Polars](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/polars): Introductory tutorial on using Polars with Hopsworks.
- [PySpark Streaming](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/pyspark_streaming): Real-time feature computation using PySpark.
- [Redshift](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/redshift): Create an External Feature Group using Redshift Storage Connector.
- [Snowflake](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/snowflake): Create an External Feature Group using Snowflake Storage Connector.
- [Weights & Biases](https://github.com/logicalclocks/hopsworks-tutorials/tree/branch-4.5/integrations/wandb): Build machine learning models with Weights & Biases.

## 📝 Feedback & Comments:
We welcome your input through:
- Our [Support Forum](https://community.hopsworks.ai/)
- This [GitHub repository](https://github.com/logicalclocks/hopsworks-tutorials)
- Email at info@hopsworks.ai