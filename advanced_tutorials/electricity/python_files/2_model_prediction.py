import hopsworks
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


project = hopsworks.login()
fs = project.get_feature_store() 


def get_feature_group(name,version=1):
    return fs.get_or_create_feature_group(
                name = name,
                version = version
            )

try:
    feature_view = fs.get_feature_view(
        name = 'electricity_feature_view',
        version = 1
    )
    
except:
    fg_weather = get_feature_group('weather_fg')
    fg_calendar = get_feature_group('calendar_fg')
    fg_electricity = get_feature_group('electricity_fg')
    
    fg_query = fg_weather.select_all()\
                        .join(
                            fg_calendar.select_all(),
                            on = ['index']
                        )\
                        .join(
                            fg_electricity.select_all(),
                            on = ['index']
                        )
    
    feature_view = fs.create_feature_view(
        name = 'electricity_feature_view',
        version = 1,
        labels = ['demand'],
        query = fg_query
    )
    
    feature_view.create_train_test_split(
        test_size = 0.2
    )
    
ms = project.get_model_serving()

deployment = ms.get_deployment("forestmodeldeploy")
deployment.start(await_running = 120)


batch = feature_view.get_batch_data()
batch.sort_values('date',inplace = True)
batch_date = batch.pop('date')
batch.drop('index', axis = 1, inplace = True)


def get_predictions(row, deployment = deployment):
    data = {
        'inputs': row.tolist()
    }
    return deployment.predict(data)

batch['predicted_demand'] = [pred['predictions'][0] for pred in batch.apply(get_predictions,axis = 1)]
batch['date'] = batch_date

def to_date(unix):
    return datetime.utcfromtimestamp(unix / 1000).strftime('%Y-%m-%d %H:%M:%S')

batch.date = pd.to_datetime(batch.date.apply(to_date))

fig,ax = plt.subplots(figsize = (16,5))

date_border = datetime.strptime('2020-10-01','%Y-%m-%d')

batch[batch.date < date_border].plot('date','predicted_demand', ax = ax)
batch[batch.date > date_border].plot('date','predicted_demand', ax = ax)

ax.legend(['Electricity Demand','Predicted Electricity Demand'])
ax.set_xlabel('Date',fontsize = 15)
ax.set_ylabel('Demand',fontsize = 15)
ax.set_title('Predicted Demand of Electricity from January 2015 to October 2020',fontsize = 20)

plt.savefig('../images/model_preds.png')
