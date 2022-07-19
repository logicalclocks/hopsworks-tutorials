# Hopsworks Tutorials
We are happy to welcome you to our collection of tutorials dedicated to exploring the fundamentals of Hopsworks and Machine Learning development. In addition to offering different types of use cases and common subjects in the field, it facilitates navigation and use of models in a production environment using Hopsworks Feature Store.

## How to run the tutorials:
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
!pip install -U hopsworks==3.0.0rc5 --quiet
```
The walkthrough and tutorials are provided in the form of Python notebooks, you will therefore need to run a jupyter environment or work within a colaboratory notebook in google; the later option might lead to some minor errors being displayed or libraries might require different library versions to work.

## Concepts:
In order to understand the tutorials you need to be familiar with general concepts of Machine Learning and Python development. You may find some useful information in the [Hopsworks documentation.](https://docs.hopsworks.ai) 

## Feedbacks & Comments:
We welcome feedbacks and suggestions, you can contact us on any of the following channels:
- Our [Support Forum](https://community.hopsworks.ai/),
- Directly on this [github repository](https://github.com/logicalclocks/hopsworks-tutorials),
- Send us an email at info@hopsworks.ai 
