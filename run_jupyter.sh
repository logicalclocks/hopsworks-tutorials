#!/bin/bash
set -e

if [ ! -f ./.installed ] | [ ! -d ./miniconda ]; then
    if [ "$(uname)" == "Darwin" ]; then
        curl -L https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-MacOSX-x86_64.sh -o Miniconda3-py38_4.8.3-x86_64.sh
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        curl -L https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh -o Miniconda3-py38_4.8.3-x86_64.sh
    fi

    chmod u+x ./Miniconda3-py38_4.8.3-x86_64.sh && ./Miniconda3-py38_4.8.3-x86_64.sh -p miniconda -b && rm Miniconda3-py38_4.8.3-x86_64.sh

    ./miniconda/bin/conda install -y --no-deps pycryptosat libcryptominisat
    ./miniconda/bin/conda config --set sat_solver pycryptosat
    ./miniconda/bin/conda update conda -y -q
    ./miniconda/bin/conda create --prefix ./miniconda/envs/hopsworks python=3.8 -y
    ./miniconda/envs/hopsworks/bin/pip install hopsworks~=3.0.0rc --no-cache-dir
    ./miniconda/envs/hopsworks/bin/pip install jupyterlab==2.3.2 jupyter
    ./miniconda/envs/hopsworks/bin/pip install scikit-learn==1.0.2

    touch .installed
fi

if [ -f ./miniconda/envs/hopsworks/bin/jupyter ]; then
    ./miniconda/envs/hopsworks/bin/jupyter trust quickstart.ipynb
    ./miniconda/envs/hopsworks/bin/jupyter lab
else
    ./miniconda/envs/hopsworks/bin/jupyter-lab
fi
