#!/bin/bash

# Update package repositories
sudo apt update

# Upgrade installed packages
sudo apt -y upgrade

# Install wget to download files
sudo apt-get install -y wget

# Install Python 3 and pip
sudo apt install -y python3-pip