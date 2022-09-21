#!/bin/bash

set -e

jupyter nbconvert --to notebook --execute scripts/cleanup-tutorials.ipynb

jupyter nbconvert --to notebook --execute quickstart.ipynb

