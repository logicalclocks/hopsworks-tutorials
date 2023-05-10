{{ config(materialized='table') }} 

SELECT *   
  FROM {YOUR_PROJECT_NAME}.{YOUR_DATASET_NAME}.{YOUR_TABLE_NAME}