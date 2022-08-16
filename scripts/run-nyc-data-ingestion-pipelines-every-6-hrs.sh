#!/bin/bash

set -e

cd ../integrations/nyc_taxi_fares/notebooks

echo "New rides data ingestion pipeline starts"
jupyter nbconvert --to notebook --execute 4.1_rides_data_ingestion.ipynb
echo "New fares data ingestion pipeline starts"
jupyter nbconvert --to notebook --execute 4.2_fares_data_ingestion.ipynb
