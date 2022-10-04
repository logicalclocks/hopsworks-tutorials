## Feature engineering functions
import requests

from math import cos, asin, sqrt, pi
from datetime import datetime, date, timedelta
from calendar import monthrange

import pandas as pd

CONST_EARTH_RADIUS = 6371       # km
CONST_EARTH_DIAMETER = 12742    # km
ELECTRICITY_PRICE_AREAS = ["SE1", "SE2", "SE3", "SE4"]
STATIONS_WITHIN_DISTANCE = 50


def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two geographical points.
    Args:
        lat1 (float): Latitude of point 1.
        lon1 (float): Longitude of point 1.
        lat2 (float): Latitude of point 2.
        lon2 (float): Longitude of point 2.
    Returns:
        float: Haversine distance in km between point 1 and 2.
    """
    p = pi / 180.0
    a = 0.5 - cos((lat2 - lat1) * p) / 2.0 + cos(lat1 * p) * cos(lat2 * p) * (1.0 - cos((lon2 - lon1) * p)) / 2
    return CONST_EARTH_DIAMETER * asin(sqrt(a))  # 2*R*asin...


def hsmi_measurment_data(measurement, period, area_name):

    if area_name == "SE1":
        city_name = "Luleå"
    elif area_name == "SE2":
        city_name = "Sundsvall"
    elif area_name == "SE3":
        city_name = "Stockholm"
    elif area_name == "SE4":
        city_name = "Malmö"

    # "Stockholm", "Malmö", "Luleå", "Sundsvall"
    city_coordinates = pd.read_csv("https://repo.hops.works/dev/davit/electricity/city_coordinates.csv")
    city_coordinates = city_coordinates[city_coordinates.City == city_name]

    #39 --> # aggpunktstemperatur --> momentanvärde, 1 gång/tim
    if measurement == "temp_per_last_hour":
        parameter = 39

    #2 -->  Lufttemperatur --> medelvärde 1 dygn, 1 gång/dygn, kl 00
    if measurement == "mean_temp_per_day":
        parameter = 2
    #18 --> Nederbörd --> 1 gång/dygn, kl 18
    elif measurement == "precipitaton_type":
        parameter = 18

    #14 --> Nederbördsmängd --> summa 15 min, 4 gånger/tim
    elif measurement == "precipitaton_amount":
        parameter = 14

    #7 --> Nederbördsmängd --> summa 1 timme, 1 gång/tim
    if measurement == "precipitaton_amount_last_hour":
        parameter = 7

    #10 --> Solskenstid --> summa 1 timme, 1 gång/tim;second
    elif measurement == "sunshine_time":
        parameter = 10

    #16 --> Total molnmängd --> momentanvärde, 1 gång/tim;percent
    elif measurement == "cloud_perc":
        parameter = 16

    #4 --> Vindhastighet  --> medelvärde 10 min, 1 gång/tim;metre per second
    elif measurement == "wind_speed":
        parameter = 4

    stations_url = f"https://opendata-download-metobs.smhi.se/api/version/latest/parameter/{parameter}.json"
    stations_resp = requests.get(url= stations_url)
    stations_pdf = pd.DataFrame(stations_resp.json()["station"])[["name","measuringStations", "id", "latitude", "longitude", "active", "key", "updated"]]
    stations_pdf = stations_pdf[stations_pdf.active == True]

    # select station in STATIONS_WITHIN_DISTANCE km radius
    stations_pdf["distance"] = stations_pdf.apply(lambda x: distance(city_coordinates.latitude.values[0], city_coordinates.longitude.values[0], x.latitude, x.longitude), axis=1)
    stations_pdf = stations_pdf[stations_pdf.distance < STATIONS_WITHIN_DISTANCE]

    if parameter in [2, 18, 5]:
        skiprows = 12
        column_names = ["from", "to", "day", measurement,"quality", "time_slice", "comment"]
    elif parameter in [10, 16, 4, 39, 14]:
        skiprows = 11
        column_names = ["day", "time", measurement,"quality", "time_slice", "comment"]

    measurment_by_city = pd.DataFrame(columns=column_names)
    for station_id in stations_pdf.id:
        if parameter in [2, 18, 5, 10, 16, 4, 39, 14]:
            url = f"https://opendata-download-metobs.smhi.se/api/version/latest/parameter/{parameter}/station/{station_id}/period/{period}/data.csv"
            try:
                if period == "corrected-archive":
                    pdf = pd.read_csv(url, sep=';', skiprows=skiprows, names= column_names)
                elif period == "latest-months":
                    pdf = pd.read_csv(url, sep=';', skiprows=skiprows, names= column_names)
                elif period == "latest-day":
                    pdf = pd.read_csv(url, sep=';', skiprows=skiprows, names= column_names)
                #pdf["area"] = area_name
                pdf = pdf[pdf["day"] > "2020-12-31"]
                measurment_by_city = pd.concat([measurment_by_city, pdf])
            except Exception:
                pass
            if parameter in [2, 18, 5]:
                measurment_by_city = measurment_by_city.drop(["from", "to"], axis=1)
            measurment_by_city = measurment_by_city.drop(["quality", "time_slice", "comment"], axis=1)
            measurment_by_city = measurment_by_city.dropna()
        return measurment_by_city


# get week days
def get_week_day(date_obj):
    return date_obj.weekday()


def all_dates_in_year(year):
    for month in range(1, 13): # Month is always 1..12
        for day in range(1, monthrange(year, month)[1] + 1):
            yield {"day": date(year, month, day).strftime("%Y-%m-%d"), "weekday": get_week_day(date(year, month, day))}


def fetch_smhi_measurements(historical_data = False):
    measurements = ["mean_temp_per_day", "wind_speed", "precipitaton_type", "precipitaton_amount", "sunshine_time", "cloud_perc"]
    meteorological_measurements = pd.DataFrame(columns=["day"])
    for measurement in measurements:
        meteorological_measurements_per_area = pd.DataFrame(columns=["day"])
        for area in ELECTRICITY_PRICE_AREAS:
            smhi_df = pd.DataFrame(columns=["day", measurement])
            if historical_data:
                smhi_df = pd.concat([smhi_df, hsmi_measurment_data(measurement, "corrected-archive", area)])
                smhi_df = pd.concat([smhi_df, hsmi_measurment_data(measurement, "latest-months", area)])
            else:
                if measurement == "mean_temp_per_day":
                    smhi_df_day = hsmi_measurment_data("temp_per_last_hour", "latest-day", area).drop("time", axis=1)
                    smhi_df_day.columns = ["day", measurement]
                    smhi_df = pd.concat([smhi_df, smhi_df_day])
                else:
                    smhi_df = pd.concat([smhi_df, hsmi_measurment_data(measurement, "latest-day", area)])
            if measurement == "mean_temp_per_day":
                smhi_df = smhi_df[smhi_df[measurement] != "Lufttemperatur"]
                smhi_df = smhi_df[smhi_df[measurement] != "Daggpunktstemperatur"]
                smhi_df[measurement] = smhi_df[measurement].map(lambda x: float(x))
                smhi_df = smhi_df.groupby(["day"]).agg({measurement: ['mean']}).reset_index()
                smhi_df.columns = ["day", measurement]
            elif measurement == "wind_speed":
                smhi_df = smhi_df[smhi_df[measurement] != "Vindhastighet"]
                smhi_df[measurement] = smhi_df[measurement].map(lambda x: float(x))
                smhi_df = smhi_df.groupby(["day"]).agg({'wind_speed': ['mean']}).reset_index()
                smhi_df.columns = ["day", f"mean_{measurement}"]
            elif measurement == "precipitaton_amount":
                smhi_df = smhi_df[smhi_df[measurement] != "Nederbördsmängd"]
                smhi_df[measurement] = smhi_df[measurement].map(lambda x: float(x))
                smhi_df = smhi_df.groupby(["day"]).agg({measurement: ['mean']}).reset_index()
                smhi_df.columns = ["day", measurement]
            elif measurement == "sunshine_time":
                smhi_df = smhi_df.groupby(["day"]).agg({measurement: ["sum"]}).reset_index()
                smhi_df.columns = ["day", f"total_{measurement}"]
            elif measurement == "cloud_perc":
                smhi_df = smhi_df[smhi_df[measurement] != "Total molnmängd"]
                smhi_df[measurement] = smhi_df[measurement].map(lambda x: float(x))
                smhi_df = smhi_df.groupby(["day"]).agg({measurement: ['mean']}).reset_index()
                smhi_df.columns = ["day", f"mean_{measurement}"]
            smhi_df.columns = [smhi_df.columns[0], f"{smhi_df.columns[1]}_{area}"]
            #meteorological_measurements_per_area = pd.concat([meteorological_measurements_per_area, smhi_df])
            meteorological_measurements_per_area = meteorological_measurements_per_area.merge(smhi_df, on=["day"], how = "outer")
        meteorological_measurements = meteorological_measurements.merge(meteorological_measurements_per_area, on=["day"], how = "outer")

    for area in ELECTRICITY_PRICE_AREAS:
        meteorological_measurements[f"precipitaton_type_{area}"] = meteorological_measurements[f"precipitaton_type_{area}"].fillna("missing")
        meteorological_measurements[f"precipitaton_amount_{area}"] = meteorological_measurements[f"precipitaton_amount_{area}"].fillna(0.0)
        meteorological_measurements[f"mean_wind_speed_{area}"] = meteorological_measurements[f"mean_wind_speed_{area}"].fillna(0.0)
        meteorological_measurements[f"total_sunshine_time_{area}"] = meteorological_measurements[f"total_sunshine_time_{area}"].fillna(0.0)
        meteorological_measurements[f"mean_cloud_perc_{area}"] = meteorological_measurements[f"mean_cloud_perc_{area}"].fillna(0.0)
        meteorological_measurements.sort_values(["day"], inplace=True)
    if historical_data:
        meteorological_measurements = meteorological_measurements[meteorological_measurements.day != datetime.now().strftime("%Y-%m-%d")]
    else:
        meteorological_measurements = meteorological_measurements[meteorological_measurements.day == datetime.now().strftime("%Y-%m-%d")]
    meteorological_measurements["timestamp"] = meteorological_measurements["day"].map(lambda x: int(float(datetime.strptime(x, "%Y-%m-%d").timestamp()) * 1000))
    return meteorological_measurements


################################################################################
def fetch_electricity_prices(historical=False):
    HOURLY = 10
    DAILY = 11
    API_URL = 'https://www.nordpoolgroup.com/api/marketdata/page/%i'
    r = requests.get(API_URL % DAILY, params={
                'currency': "SEK",
                'endDate': datetime.now().strftime("%d-%m-%Y"),
            })

    areas=['SE1', 'SE2', 'SE3', 'SE4']
    areas_data = {}
    areas_data[areas[0]] = {}

    currency = r.json()['currency']
    data = r.json()['data']
    start_time = data['DataStartdate']
    end_time = data['DataEnddate']
    updated = data['DateUpdated']

    area_price_list = []
    for r in data['Rows']:
        for c in r['Columns']:
            if c['Name'] in areas:
                area_price_list.append({"start_time": r["StartTime"], "end_time": r["EndTime"], "area": c["Name"], "price":c['Value']})
    pdf = pd.DataFrame(area_price_list)
    pdf["day"] = pdf["start_time"].map(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').strftime("%Y-%m-%d"))
    pdf = pdf.drop(["start_time", "end_time"], axis=1)
    pdf.price = pdf.price.map(lambda x: float(x.replace(" ", "").replace(",", ".")))
    pdf = pdf.groupby(["day", "area"]).agg({'price': ['mean']}).reset_index()
    pdf.columns = ["day", "area", "price"]
    if not historical:
        today = (date.today()).strftime("%Y-%m-%d")
        pdf = pdf[pdf.day == today]

    SE1 = pdf[pdf.area == "SE1"].drop(["area"], axis=1)
    SE1.columns = ["day", "price_se1"]
    SE2 = pdf[pdf.area == "SE2"].drop(["area"], axis=1)
    SE2.columns = ["day", "price_se2"]
    SE3 = pdf[pdf.area == "SE3"].drop(["area"], axis=1)
    SE3.columns = ["day", "price_se3"]
    SE4 = pdf[pdf.area == "SE4"].drop(["area"], axis=1)
    SE4.columns = ["day", "price_se4"]

    pdf = SE1.merge(SE2, on=["day"], how = "outer")
    pdf = pdf.merge(SE3, on=["day"], how = "outer")
    pdf = pdf.merge(SE4, on=["day"], how = "outer")

    pdf["timestamp"] = pdf["day"].map(lambda x: int(float(datetime.strptime(x, "%Y-%m-%d").timestamp()) * 1000))
    return pdf
