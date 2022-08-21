#!/bin/bash

set -e

cd ../advanced_tutorials/nyc_taxi_fares

echo "$PWD"

echo "Remodelling pipeline starts."

jupyter nbconvert --to notebook --execute 3_model_training.ipynb
