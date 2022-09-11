#!/bin/bash

echo "$PWD"

set -e

echo "Running batch prediction pipeline"

cd advanced_tutorials/electricity 

jupyter nbconvert --to notebook --execute 5_batch_predictions.ipynb