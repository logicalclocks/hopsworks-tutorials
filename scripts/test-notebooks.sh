#!/bin/bash

set -e

# Remove any FGs, FVs, Models, Deployments
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute scripts/cleanup-tutorials.ipynb

# Quickstart
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute quickstart.ipynb

# fraud batch
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute fraud_batch/1_feature_groups.ipynb 
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute fraud_batch/2_feature_view_creation.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute fraud_batch/3_model_training.ipynb

# fraud online
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute fraud_online/1_feature_groups.ipynb 
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute fraud_online/2_feature_view_creation.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute fraud_online/3_model_training.ipynb


# churn
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute churn/1_feature_groups.ipynb 
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute churn/2_feature_view_creation.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute churn/3_model_training.ipynb


# Great Expectations
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute integrations/great_expectations/Great_Expectations_Hopsworks_Concepts.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute integrations/great_expectations/fraud_batch_data_validation.ipynb


# W&B
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute integrations/wandb/1_feature_groups.ipynb 
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute integrations/wandb/2_feature_view_creation.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute integrations/wandb/3_model_training.ipynb


# Electricity Prices
cd advanced_tutorials/electricity
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 1_backfill_feature_groups.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 2_feature_pipeline.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 3_feature_views_and_training_dataset.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 4_model_training.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 5_batch_predictions.ipynb

cd ../..

# NYC Taxi Trips
cd advanced_tutorials/nyc_taxi_fares/

jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 1_backfill_feature_groups.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 2_features_pipeline.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 3_feature_view_and_dataset_creation.ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=1200  --to notebook --execute 4_model_training_and_registration.ipynb


cd ../..



