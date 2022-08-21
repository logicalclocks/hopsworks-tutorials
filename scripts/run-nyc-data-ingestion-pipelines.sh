#!/bin/bash

set -e

echo "$PWD"

cd advanced_tutorials/nyc_taxi_fares

echo "New rides data ingestion pipeline starts"
jupyter nbconvert --to notebook --execute 1.1_rides_fg.ipynb
echo "New fares data ingestion pipeline starts"
jupyter nbconvert --to notebook --execute 1.2_fares_fg.ipynb
