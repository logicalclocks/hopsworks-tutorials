
import requests
import hopsworks
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re


def parse_data(parser,tag: str, class_: str):
    new_data = []
    data = parser.find_all(tag,class_)
    for el in data:
        new_data.append(el.text)
    
    return new_data


def parse_page(page_name):
    response = requests.get(f'https://www.elbruk.se/timpriser-{page_name}')
    content = response.content
    
    parser = BeautifulSoup(content, 'html.parser')
    
    data = parse_data(parser,'div','info-box-content')
    electricity_prices = [float(re.findall(r'\d+\,\d+',info.split('\n')[2])[0].replace(',','.')) for info in data[:4]]
    
    return electricity_prices


def timestamp_2_time(x):
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d %H:%M')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


page_names = ['se1-lulea','se2-sundsvall','se3-stockholm','se4-malmo']

data = [[datetime.now().strftime("%Y-%m-%d %H:%M"),page_name.split('-')[1].capitalize(),*parse_page(page_name)] for page_name in page_names]

data


columns = [
    'date',
    'city',
    'price_day',
    'price_current',
    'price_min',
    'price_max'
]


dataframe = pd.DataFrame(
    data = data,
    columns = columns
)
dataframe.date = dataframe.date.apply(timestamp_2_time)

dataframe.head()


project = hopsworks.login()

fs = project.get_feature_store() 


def retrieve_feature_group(name='electricity_prices',fs=fs):
    feature_group = fs.get_feature_group(
        name=name,
        version=1
    )
    return feature_group

def create_feature_group(data,name='electricity_prices',fs=fs):
    
    feature_group = fs.get_or_create_feature_group(
        name=name,
        description = 'Characteristics of each day',
        version = 1,
        primary_key = ['index'],
        online_enabled = True,
        event_time = ['date']
    )
        
    feature_group.insert(data.reset_index())
    
    return feature_group



try:
    feature_group = retrieve_feature_group()
    feature_group.insert(dataframe.reset_index())
    
except:
    feature_group = create_feature_group(dataframe)

