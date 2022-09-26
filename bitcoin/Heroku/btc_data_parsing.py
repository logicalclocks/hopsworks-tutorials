from unicorn_binance_rest_api.manager import BinanceRestApiManager as Client
import datetime
import pandas as pd
import os #provides ways to access the Operating System and allows us to read the environment variables

from settings import LOCALLY


if LOCALLY:
    from dotenv import load_dotenv
    load_dotenv()

    
def timestamp_2_time(x):
    dt_obj = datetime.datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


def get_client():
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    return Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


def get_data(since_this_date=None, until_this_date=datetime.datetime.now(), number_of_days_ago=None, crypto_pair="BTCUSDT"):
    client = get_client()
    
    # Calculate the timestamps for the binance api function
    if since_this_date:
        since_this_date += datetime.timedelta(days=1)
    if number_of_days_ago:
        until_this_date = datetime.datetime.now()
        since_this_date = until_this_date - datetime.timedelta(days=number_of_days_ago)
    # Execute the query from binance - timestamps must be converted to strings !
    candle = client.get_historical_klines(crypto_pair, Client.KLINE_INTERVAL_1DAY, str(since_this_date), str(until_this_date))

    # Create a dataframe to label all the columns returned by binance so we work with them later.
    df = pd.DataFrame(candle, columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
    # as timestamp is returned in ms, let us convert this back to proper timestamps.
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime("%Y-%m-%d %H:%M:%S")
    df.set_index('dateTime', inplace=True)
    # now returns ALL columns
    return df.drop(['closeTime','ignore'],axis = 1)


def parse_btc_data(last_date=None, number_of_days_ago=None):
    if number_of_days_ago:
        number_of_days_ago += 1
    df = get_data(since_this_date=last_date, until_this_date=datetime.datetime.now(),
                  number_of_days_ago=number_of_days_ago)
    df.index.name = 'date'
    df.reset_index(inplace = True)
    df.columns = [*df.columns[:6],'quote_av','trades','tb_base_av','tb_quote_av']
    cols = [*df.columns]
    cols.remove('date')
    cols.remove('trades')
    df[cols] = df[cols].apply(lambda x: x.apply(float))
    df.trades = df.trades.apply(int)
    df['unix'] = pd.to_datetime(df.date).apply(timestamp_2_time)
    return df
                                          