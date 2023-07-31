# <span style="font-width:bold; font-size: 3rem; color:#1EB182;"><img src="../images/icon102.png" width="38px"></img> **Hopsworks Feature Store** </span><span style="font-width:bold; font-size: 3rem; color:#333;">Quick Start - Fraud Online Tutorial</span>

<span style="font-width:bold; font-size: 1.4rem;"> This is a quick-start of the Hopsworks Feature Store; using a fraud use case you will load data into the feature store, create two feature groups from which we will make a training dataset, and train a model. This is an <b>online use case</b>, it will give you a high-level view of how to use our python APIs and the UI to navigate the feature groups, use them to create feature views, training datasets, save and deploy models using Hopsworks Feature Store. </span>

## **🗒️ This Quick introduction is divided into the next parts:**
1. **Feature Pipeline**: How to load, engineer and create feature groups.
2. **Training Pipeline**: How to build a feature view, training dataset split, train, save and deploy a model.
3. **Inference Pipeline**: How to retrieve a trained model from the model registry and use it for online inference.
4. **Streamlit App**: Build a Streamlit App fro interactive predictions.

## Prerequisites
To run this tutorial, you need an account on Hopsworks. You can create a new account at  [app.hopsworks.ai](https://app.hopsworks.ai).
In the notebook you will be prompted with a link to generate an API token to interact with your Hopsworks account.

#  <span style="font-width:bold; font-size: 3rem; color:#1EB182;">Hopsworks: Main Concepts</span>
You may refer to the concept documentation on [docs.hopsworks.ai](https://docs.hopsworks.ai/concepts/)  for an extensive overview of all the concepts and abstractions in the feature store.
Below are the concepts covered in this quick-start;

## Feature Store

The [Feature Store](https://www.hopsworks.ai/feature-store) is a data management system that allows data scientists and data engineers to efficiently collaborate on projects.

An organization might have separate data pipelines for each and every model they train. In many cases, this results in duplicate work, as the pipelines typically share some preprocessing steps in common. Consequently, changes in some preprocessing steps would result in even more duplicate work, and potential inconsistencies between pipelines.

Moreover, once a model has been deployed we need to make sure that online data is processed in the same way as the training data. The Feature Store streamlines the data pipeline creation process by putting all the feature engineering logic of a project in the same place. The built-in version control enables them to work seamlessly with different versions of features and datasets.

Another advantage of having a feature store set up is that you can easily do "time travel" and recreate training data as it would have looked at some point in the past. This is very useful when, for example, benchmarking recommendation systems or assessing concept drift.

In short, a feature store enables data scientists to reuse features across different experiments and tasks and to recreate datasets from a given point in time.

In Hopsworks, the `hsfs` library is the Python interface to the feature store.

### Feature Group

A Feature Group is a collection of conceptually related features that typically originate from the same data source. It is really up to the user (perhaps a data scientist) to decide which features should be grouped together into a feature group, so the process is subjective. Apart from conceptual relatedness or stemming from the same data source, another way to think about a feature group might be to consider features that are collected at the same rate (e.g. hourly, daily, monthly) to belong to the same feature group.

A feature group is stored in the feature store and can exist in several versions. New data can be freely appended to a feature group, as long as it conforms to the data validation rules the user has set up.

### Data Validation

The data might not conform to the data schema we have defined. It could happen that a numerical feature is given as a string, or that a feature that should be a positive number is given as a negative number. For example, we might decide that a transaction amount must be positive.

In Hopsworks you can define feature expectations, which ensures that the data adheres to a specified format. These expectations can be attached to a feature group either during the creation of the feature group or after the feature group has been created.

### Feature Engineering

Typically it does not suffice to train a model using raw data sources alone. There can for instance be data problems such as missing values and duplicate entries that need to be dealt with. Moreover, model training could be facilitated by preprocessing raw features, or creating new features using raw features.

Feature engineering can be considered a whole subfield by itself and there are general resources such as [Feature Engineering and Selection: A Practical Approach for Predictive Models](https://www.amazon.com/Feature-Engineering-Selection-Practical-Predictive-dp-1138079227/dp/1138079227/ref=as_li_ss_tl?_encoding=UTF8&me=&qid=1588630415&linkCode=sl1&tag=inspiredalgor-20&linkId=f3f8d9f56031a030893aad8fc684a800&language=en_US) and various Python libraries for feature engineering such as [tsfresh](https://tsfresh.readthedocs.io/en/latest/) for time series or [featuretools](https://www.featuretools.com/) which also handles relational data.

Engineered features are typically also stored in feature groups in the feature store.


### Preparing Data for Model Training

Hopsworks makes it easy to create datasets for model training.

In the Hopsworks framework, training datasets are immutable in the sense that, in contrast to feature groups, you cannot append data to them after they have been created. However, you *can* have different *versions* of the same training dataset.

Often, a training dataset will be created by running a query to join the feature groups of interest. This query is saved as metadata in the dataset, which makes it easy to see the dependencies between the dataset and the feature groups it originates from. The Hopsworks UI contains a dataset provenance graph that shows this.

<!-- Moreover, you can download the dataset in a format compatible with the framework you're working with, e.g. tfrecords, numpy, csv... -->
