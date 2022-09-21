#!/bin/bash

set -e

jupyter nbconvert --to notebook --execute scripts/cleanup-tutorials.ipynb


# fraud batch

jupyter nbconvert --to notebook --execute fraud_batch/1_feature_groups.ipynb 
jupyter nbconvert --to notebook --execute fraud_batch/2_feature_view_creation.ipynb
jupyter nbconvert --to notebook --execute fraud_batch/3_model_training.ipynb

# fraud online
jupyter nbconvert --to notebook --execute fraud_online/1_feature_groups.ipynb 
jupyter nbconvert --to notebook --execute fraud_online/2_feature_view_creation.ipynb
jupyter nbconvert --to notebook --execute fraud_online/3_model_training.ipynb


# churn
jupyter nbconvert --to notebook --execute churn/1_feature_groups.ipynb 
jupyter nbconvert --to notebook --execute churn/2_feature_view_creation.ipynb
jupyter nbconvert --to notebook --execute churn/3_model_training.ipynb


# Great Expectations
jupyter nbconvert --to notebook --execute integrations/great_expectations/Great_Expectations_Hopsworks_Concepts.ipynb
jupyter nbconvert --to notebook --execute integrations/great_expectations/fraud_batch_data_validation.ipynb


# W&B
jupyter nbconvert --to notebook --execute integrations/wandb/1_feature_groups.ipynb 
jupyter nbconvert --to notebook --execute integrations/wandb/2_feature_view_creation.ipynb
jupyter nbconvert --to notebook --execute integrations/wandb/3_model_training.ipynb

# Quickstart

jupyter nbconvert --to notebook --execute quickstart.ipynb
