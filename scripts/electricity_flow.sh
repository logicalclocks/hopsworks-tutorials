set -e

echo "$PWD"

cd advanced_tutorials/electricity/python_files

echo "Air Quality ingestion pipeline starts"
python3 electricity_parsing.py
