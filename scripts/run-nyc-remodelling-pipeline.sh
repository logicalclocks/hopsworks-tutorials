#!/bin/bash

set -e
echo "$PWD"

cd advanced_tutorials/nyc_taxi_fares/python_files


echo "Remodelling pipeline starts."

python3 3_model_training.py
