#!/bin/bash

set -e

echo "$PWD"

cd advanced_tutorials/nyc_taxi_fares

echo "Data generation and ingestion pipeline starts"
jupyter nbconvert --to notebook --execute 2_features_pipeline.ipynb
