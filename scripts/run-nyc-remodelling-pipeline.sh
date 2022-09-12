#!/bin/bash

set -e
echo "$PWD"

cd advanced_tutorials/nyc_taxi_fares


echo "Remodelling pipeline starts."

jupyter nbconvert --to notebook --execute 4_model_training_and_registration.ipynb
