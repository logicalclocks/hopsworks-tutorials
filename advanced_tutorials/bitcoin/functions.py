import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from unicorn_binance_rest_api.manager import BinanceRestApiManager as Client
import os

from plotly import tools
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go

import warnings
warnings.filterwarnings('ignore')

import json
import io
import re
import time
import os.path
import math
from dateutil import parser
import datetime
from tqdm import tnrange, tqdm_notebook, tqdm

from textblob import TextBlob
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm import tnrange, tqdm_notebook, tqdm
from sklearn import preprocessing

import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')


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


def parse_btc_data(last_date=None, number_of_days_ago=5):
    df = get_data(since_this_date=last_date, until_this_date=datetime.datetime.now(),
                  number_of_days_ago=number_of_days_ago + 1)
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

    df['signal'] = np.where(df['mean_7_days'] > df['mean_56_days'], 1.0, 0.0)

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


def get_api():
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")

    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    authentificate = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    authentificate.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(authentificate, wait_on_rate_limit=True)

    return api


twitter_accounts = ['APompliano', 'AltcoinSara', 'BVBTC', 'BitBoy_Crypto',
                     'CamiRusso', 'CryptoCred', 'CryptoWendyO', 'ErikVoorhees',
                     'Excellion', 'IvanOnTech', 'KennethBosak', 'LayahHeilpern',
                     'Matt_Hougan', 'Natbrunell', 'Nicholas_Merten', 'RAFAELA_RIGO_',
                     'SBF_FTX', 'SatoshiLite', 'SheldonEvans', 'TimDraper',
                     'ToneVays', 'VitalikButerin', 'WhalePanda', 'aantonop',
                     'aantop', 'adam3us', 'bgarlinghouse', 'bhorowitz', 'brockpierce',
                     'cz_binance', 'danheld', 'elonmusk', 'ethereumJoseph',
                     'girlgone_crypto', 'justinsuntron', 'officialmcafee',
                     'rogerkver', 'saylor', 'thebrianjung']


def get_last_tweets(query="#btc OR #bitcoin from:", twitter_accounts=twitter_accounts, n_tweets=1000):
    """
    Returns a DataFrame with tweets of specific topic (use query argument), ~ for last 9 days.
    Iterates through every twitter account from 'twitter_accounts' list

    - query:
        str, more info, operators for Twitter API, examples:
            https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators

    - twitter_accounts:
     list, list of Twitter usernames, whose tweets we are going to parse.
    - n_tweets:
        int, number of tweets that we want to retrieve per each account.
        (often smaller amount will be retrieved because of Twitter timerange restrictions)
    """

    df = pd.DataFrame(columns=["created_at", "full_text"])

    api = get_api()

    for twitter_acc in twitter_accounts:

        search_query = query + twitter_acc

        #date_until = "2022-06-26"
        tweets_cursor = tweepy.Cursor(api.search_tweets,
                           q=search_query,
                           lang="en",
                           tweet_mode="extended",
                           #until=date_until
                           ).items(n_tweets)
        json_data = [r._json for r in tweets_cursor]

        try:
            temp_df = pd.json_normalize(json_data) [["created_at", "full_text"]]
        except KeyError:
            continue


        temp_df.full_text = temp_df.full_text.apply(lambda x: basic_cleaning(x))

        df = pd.concat([df, temp_df])

    df = df.sort_values(by=["created_at"])
    df.reset_index(drop=True, inplace=True)
    df['created_at'] = pd.to_datetime(df['created_at'])

    df = df.rename(columns={"created_at":"date", "full_text":"text"})

    return df

def basic_cleaning(full_text):
    """
    Some tweets (if they are replies) start with "RT @twitter_user: blabla..."
    Some tweets start with "@TwitterUser blabla..."
    So I will delete these pieces and leave only payloads.
    """

    if full_text[:2] == "RT":
        return " ".join(full_text.split()[2:])
    if full_text[0] == "@":
        words = full_text.split()
        return " ".join([word for word in words if not word.startswith("@")])

    return full_text


def clean_text2(df):
    """Second cleaning using 'nltk' module. Processes 'text' feature. """

    stop_words = nltk.corpus.stopwords.words(['english'])
    lem = nltk.WordNetLemmatizer()

    def cleaning(data):
        # remove urls
        tweet_without_url = re.sub(r'http\S+',' ', data)

        # remove hashtags
        tweet_without_hashtag = re.sub(r'#\w+', ' ', tweet_without_url)

        # Remove mentions and characters that not in the English alphabets
        tweet_without_mentions = re.sub(r'@\w+',' ', tweet_without_hashtag)
        precleaned_tweet = re.sub('[^A-Za-z]+', ' ', tweet_without_mentions)

        # Tokenize
        tweet_tokens = nltk.TweetTokenizer().tokenize(precleaned_tweet)

        # Remove Puncs
        tokens_without_punc = [w for w in tweet_tokens if w.isalpha()]

        # Removing Stopwords
        tokens_without_sw = [t for t in tokens_without_punc if t not in stop_words]

        # lemma
        text_cleaned = [lem.lemmatize(t) for t in tokens_without_sw]

        # Joining
        return " ".join(text_cleaned)

    df['cleaned_tweets'] = df['text'].apply(cleaning)

    return df


def textblob_processing(df_input):
    """
    Applies TextBlob sentiment analisys to 'cleaned_tweets' feature in the DataFrame df
    """
    df = df_input.copy()
    df = clean_text2(df)

    def getSubjectivity(tweet):
        return TextBlob(tweet).sentiment.subjectivity

    def getPolarity(tweet):
        return TextBlob(tweet).sentiment.polarity

    correct_dates = df['date'].copy()
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    df.cleaned_tweets = df.cleaned_tweets.astype(str)

    df['subjectivity'] = df['cleaned_tweets'].apply(getSubjectivity)
    df['polarity'] = df['cleaned_tweets'].apply(getPolarity)

    df.date = correct_dates
    df.date = pd.to_datetime(df.date)
    df = df.set_index("date")
    df = df.resample('1D').sum()
    df = df[["subjectivity", "polarity"]].reset_index()

    df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['unix'] = df.date.apply(timestamp_2_time)

    return df


def vader_processing(df_input):
    """
    Takes a DataFrame with 'text' column (cleaned using 'clean_text1' function) and
    returns a DataFrame with VADER-analized score.
    """
    df = df_input.copy()
    analyzer = SentimentIntensityAnalyzer()
    compound = []
    for i,s in enumerate(tqdm(df['text'], position=0, leave=True)):
        # print(i,s)
        vs = analyzer.polarity_scores(str(s))
        compound.append(vs["compound"])
    df["compound"] = compound
    df.date = pd.to_datetime(df.date)
    df = df.set_index("date")[["compound"]]
    df = df.resample('1D').sum()
    df = df.reset_index()
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['unix'] = df.date.apply(timestamp_2_time)

    return df
