#!/bin/bash

set -e
echo "$PWD"

cd advanced_tutorials/nyc_taxi_fares


echo "Remodelling pipeline starts."

jupyter nbconvert --to notebook --execute 3_model_training.ipynb
