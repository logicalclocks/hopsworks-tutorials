#!/bin/bash

set -e

echo "Running feature backfill pipeline"
cd advanced_tutorials/electricity 

jupyter nbconvert --to notebook --execute 2_feature_pipeline.ipynb