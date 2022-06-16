#!/bin/bash
set -e

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

./miniconda/envs/hopsworks/bin/pip install jupyterlab==2.2.8 'git+https://github.com/logicalclocks/feature-store-api@master#egg=hsfs[python]&subdirectory=python' 'git+https://github.com/logicalclocks/hopsworks-api@main#egg=hopsworks&subdirectory=python' --force-reinstall

./miniconda/envs/hopsworks/bin/jupyter trust quickstart.ipynb
./miniconda/envs/hopsworks/bin/jupyter lab
