#!/bin/bash

curl -LO https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh

bash Miniconda3-py38_4.8.3-Linux-x86_64.sh -p miniconda3 -b

./miniconda3/bin/conda install -y --no-deps pycryptosat libcryptominisat
./miniconda3/bin/conda config --set sat_solver pycryptosat
./miniconda3/bin/conda update conda -y -q
./miniconda3/bin/conda create --prefix ./miniconda3/envs/hopsworks python=3.8 -y

./miniconda3/envs/hopsworks/bin/pip install -U jupyterlab==2.2.8 'git+https://github.com/logicalclocks/feature-store-api@master#egg=hsfs[python]&subdirectory=python' 'git+https://github.com/logicalclocks/hopsworks-api@main#egg=hopsworks&subdirectory=python' --force-reinstall

./miniconda3/envs/hopsworks/bin/jupyter lab


