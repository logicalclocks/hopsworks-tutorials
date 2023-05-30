import os
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from unicorn_binance_rest_api.manager import BinanceRestApiManager as Client
from dotenv import load_dotenv
load_dotenv()


def get_hours(unix):
    return unix / 3600000 % 24


def fix_unix(unix):
    if get_hours(unix) == 23.0:
        return unix - 3600000
    elif get_hours(unix) == 21.0:
        return unix + 3600000
    return unix


def convert_unix_to_date(x):
    x //= 1000
    x = datetime.datetime.fromtimestamp(x)
    return datetime.datetime.strftime(x, "%Y-%m-%d")


def convert_date_to_unix(x):
    try:
        dt_obj = datetime.datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    except:
        dt_obj = datetime.datetime.strptime(str(x), '%Y-%m-%d')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


def get_client():
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    return Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


def get_data(start_date=None, end_date=None,
             number_of_days_ago=None,
             crypto_pair="BTCUSDT"):
    
    client = get_client()

    # Calculate the timestamps for the binance api function
    if number_of_days_ago:
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=number_of_days_ago)
        
    # Execute the query from binance - timestamps must be converted to strings !
    candle = client.get_historical_klines(crypto_pair,
                                          Client.KLINE_INTERVAL_1DAY,
                                          str(start_date), str(end_date))

    # Create a dataframe to label all the columns returned by binance so we work with them later.
    df = pd.DataFrame(candle, columns=['dateTime', 'open', 'high', 'low', 'close',
                                       'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades',
                                       'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
    
    # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime("%Y-%m-%d %H:%M:%S")
    df.set_index('dateTime', inplace=True)
    # now returns ALL columns
    return df.drop(['closeTime','ignore'],axis = 1)


def parse_btc_data(start_date=None, end_date=None, number_of_days_ago=None):
    today = str(datetime.date.today())
    if start_date and not end_date:
        end_date = today
    elif end_date in ["today", "now"]:
        end_date = today

    if number_of_days_ago:
        df = get_data(number_of_days_ago=number_of_days_ago + 1,
                      crypto_pair="BTCUSDT")
    elif start_date and end_date:
        df = get_data(start_date=start_date,
                      end_date=end_date,
                      crypto_pair="BTCUSDT")
    
    df.index.name = 'date'
    df.reset_index(inplace = True)
    df.columns = [*df.columns[:6],'quote_av','trades','tb_base_av','tb_quote_av']
    cols = [*df.columns]
    cols.remove('date')
    cols.remove('trades')
    df[cols] = df[cols].apply(lambda x: x.apply(float))
    df.trades = df.trades.apply(int)
    df['unix'] = pd.to_datetime(df.date).apply(convert_date_to_unix)
    return df


def moving_average(df,window = 7):
    df[f'mean_{window}_days'] = df['close'].rolling(window = window).mean()
    return df


def moving_std(df,window):
    df[f'std_{window}_days'] = df.close.rolling(window = window).std()
    return df


def exponential_moving_average(df, window):
    df[f'exp_mean_{window}_days'] = df.close.ewm(span = window).mean()
    return df


def exponential_moving_std(df, window):
    df[f'exp_std_{window}_days'] = df.close.ewm(span = window).std()
    return df


def momentum_price(df,window):
    '''
     It is the rate of acceleration of a security's price or volume; the speed at which the price is changing.
    '''
    df[f'momentum_{window}_days'] = df.close.diff(window)
    return df


def rate_of_change(df,window):
    '''
     Assets with higher ROC values are considered more likely to be overbought;Lower - likely to be oversold.
    '''
    M = df.close.diff(window - 1)
    N = df.close.shift(window - 1)
    df[f'rate_of_change_{window}_days'] = (M / N) * 100
    return df


def strength_index(df, period):
    '''
     It is a momentum indicator that measures the magnitude of recent price changes
     to evaluate overbought or oversold conditions in the price of a stock or other asset.
     Ranging from [0,100].
     Asset -> 70: asset deemed overbought.
     Asset -> 30: asset getting undersold & undervalued.
    '''
    delta = df.close.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period-1]] = np.mean( u[:period] )
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] )
    d = d.drop(d.index[:(period-1)])
    rs = u.ewm(com = period-1, adjust = False).mean() / d.ewm(com = period-1, adjust = False).mean()
    df[f'strength_index_{period}_days'] = 100 - 100 / (1 + rs)
    return df


def process_btc_data(df):
    df = moving_average(df,7)
    df = moving_average(df,14)
    df = moving_average(df,56).fillna(0)

    for i in [7, 14, 56]:
        for func in [moving_std, exponential_moving_average,
                     exponential_moving_std,
                     momentum_price, rate_of_change,
                     strength_index]:
            df = func(df, i).fillna(0)

    df.date = pd.to_datetime(df.date)
    return df


def get_price_plot(data):
    fig = go.Figure()
    trace1 = go.Scatter(
        x = data.reset_index()['date'],
        y = data['close'].astype(float),
        mode = 'lines',
        name = 'Close'
    )

    layout = dict(
        title = 'Historical Bitcoin Prices',
     xaxis = dict(
         rangeslider=dict(visible = True), type='date'
       )
    )
    fig.add_trace(trace1)
    fig.update_layout(layout)
    fig.update_traces(hovertemplate = 'Data: %{x} <br>Price: %{y}')
    fig.update_yaxes(fixedrange=False)

    return fig


def get_volume_plot(data):
    fig = go.Figure()
    trace1 = go.Scatter(
        x = data.reset_index()['date'],
       y = data['volume'],
       mode = 'lines',
       name = 'Bitcoin Volume'
    )

    layout = dict(
        title = 'Historical Bitcoin Volume',
        xaxis = dict(
           rangeslider=dict(
               visible = True
            ),
            type='date'
     )
    )

    fig.add_trace(trace1)
    fig.update_layout(layout)
    fig.update_traces(hovertemplate = 'Data: %{x} <br>Volume: %{y}')

    return fig
