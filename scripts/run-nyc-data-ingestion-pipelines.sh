#!/bin/bash

set -e

echo "$PWD"

cd advanced_tutorials/nyc_taxi_fares/python_files

echo "New rides data ingestion pipeline starts"
python3 1.1_rides_fg.py
echo "New fares data ingestion pipeline starts"
python3 1.2_fares_fg.py
