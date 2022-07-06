#!/bin/bash
set -e

if ! gcc -v &> /dev/null
then
    echo "Could not find gcc, please install it first"
    exit 1
fi

if [ ! -f ./.installed ] | [ ! -d ./miniconda ]; then
    if [ "$(uname)" == "Darwin" ]; then
      if [ $(uname -m) == 'arm64' ]; then
        curl -L https://repo.anaconda.com/miniconda/Miniconda3-py38_4.12.0-MacOSX-arm64.sh -o Miniconda3-py38_4.12.0-x86_64.sh
      elif [ $(uname -m) == 'x86_64' ]; then
        curl -L https://repo.anaconda.com/miniconda/Miniconda3-py38_4.12.0-MacOSX-x86_64.sh -o Miniconda3-py38_4.12.0-x86_64.sh
      fi
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        curl -L https://repo.anaconda.com/miniconda/Miniconda3-py38_4.12.0-Linux-x86_64.sh -o Miniconda3-py38_4.12.0-x86_64.sh
    fi

    chmod u+x ./Miniconda3-py38_4.12.0-x86_64.sh && ./Miniconda3-py38_4.12.0-x86_64.sh -p miniconda -b && rm Miniconda3-py38_4.12.0-x86_64.sh

    ./miniconda/bin/conda install -y --no-deps pycryptosat libcryptominisat
    ./miniconda/bin/conda config --set sat_solver pycryptosat
    ./miniconda/bin/conda update conda -y -q
    ./miniconda/bin/conda create --prefix ./miniconda/envs/hopsworks python=3.8 -y
    ./miniconda/envs/hopsworks/bin/pip install hopsworks==3.0.0rc5 --no-cache-dir
    ./miniconda/envs/hopsworks/bin/pip install jupyterlab==2.3.2 jupyter scikit-learn==1.0.2 matplotlib==3.5.2 seaborn==0.11.2

    touch ./.installed
fi

# Set environment variable for hopsworks.login()
if [ -f ./.hw_api_key ]; then
    export HOPSWORKS_API_KEY=`cat ./.hw_api_key`
fi

if [ -f ./miniconda/envs/hopsworks/bin/jupyter ]; then
    ./miniconda/envs/hopsworks/bin/jupyter trust quickstart.ipynb
    ./miniconda/envs/hopsworks/bin/jupyter lab
else
    ./miniconda/envs/hopsworks/bin/jupyter-lab
fi
