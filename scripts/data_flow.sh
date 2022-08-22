set -e

echo "$PWD"

cd advanced_tutorials/electricity/python_files

echo "New Weather data ingestion pipeline starts"
python3 1_weather_fg.py

echo "New Calendar data ingestion pipeline starts"
python3 1_calendar_fg.py

echo "New Electricity data ingestion pipeline starts"
python3 1_electricity_fg.py