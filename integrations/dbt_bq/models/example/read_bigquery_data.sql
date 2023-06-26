{{ config(materialized='table') }} 

SELECT 
  city_name,
  base_time,
  forecast_hr,
  temperature,
  relative_humidity,
  weather_code,
  wind_speed,
  wind_direction,
  ROW_NUMBER() OVER () AS index_column,
  EXTRACT(HOUR FROM base_time) AS hour,
  EXTRACT(DAY FROM base_time) AS day,
  temperature - LAG(temperature) OVER (
    PARTITION BY city_name 
        ORDER BY base_time
        ) AS temperature_diff,
  CASE
    WHEN wind_speed < 2.5 THEN 'Low'
    WHEN wind_speed < 5.0 THEN 'Moderate'
    WHEN wind_speed < 7.5 THEN 'High'
    ELSE 'Very High'
  END AS wind_speed_category
FROM {YOUR_PROJECT_NAME}.{YOUR_DATASET_NAME}.{YOUR_TABLE_NAME}