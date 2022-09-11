## Feature engineering functions
import requests

from datetime import datetime, date, timedelta

import pandas as pd

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

