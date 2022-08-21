#!/bin/bash

set -e

echo "Remodelling pipeline starts."
cd notebooks

jupyter nbconvert --to notebook --execute 5_model_refitting.ipynb
