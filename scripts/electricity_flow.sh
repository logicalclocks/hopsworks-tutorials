set -e

echo "$PWD"

cd air_quality/python_files

echo "Air Quality ingestion pipeline starts"
python3 electricity_parsing.py
