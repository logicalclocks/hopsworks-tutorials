#!/bin/bash

export HOPSWORKS_API_KEY=$(cat api-key.txt)

python -m streamlit run streamlit-image.py
