import json
import re
import time
import os.path
import math

import numpy as np
import pandas as pd

import datetime
from dateutil import parser

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

from tqdm import tnrange, tqdm_notebook, tqdm

import warnings
warnings.filterwarnings('ignore')

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk.stem.wordnet import WordNetLemmatizer


def timestamp_2_time(x):
    dt_obj = datetime.datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


def fill_gap(df, last_date, fill_with=0):
    last_date += datetime.timedelta(days=1)
    df['date'] = pd.to_datetime(df['date'])
    df = (df.set_index('date')
          .reindex(pd.date_range(last_date, datetime.datetime.now(), freq='D'))
          .rename_axis(['date'])
          .fillna(0)
          .reset_index())
    return df


def clean_text1(df):
    """First cleaning"""

    for i,s in enumerate(tqdm(df['text'],position=0, leave=True)):
        text = str(df.loc[i, 'text'])
        text = text.replace("#", "")
        text = re.sub('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', '', text, flags=re.MULTILINE)
        text = re.sub('@\\w+ *', '', text, flags=re.MULTILINE)
        df.loc[i, 'text'] = text
    return df


def vader_processing(df, last_date):
    """
    Takes a DataFrame with 'text' column (cleaned using 'clean_text1' function) and
    returns a DataFrame with VADER-analized score.
    """

    df = clean_text1(df)

    analyzer = SentimentIntensityAnalyzer()
    compound = []
    for i,s in enumerate(tqdm(df['text'], position=0, leave=True)):
        # print(i,s)
        vs = analyzer.polarity_scores(str(s))
        compound.append(vs["compound"])
    df["compound"] = compound
    df = df.set_index("date")[["compound"]]
    df = df.resample('1D').sum()
    df = df.reset_index()
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = fill_gap(df, last_date)
    df['unix'] = df.date.apply(timestamp_2_time)

    df["date"] = df["date"].astype(str)
    
    return df



def clean_text2(df):
    """Second cleaning using 'nltk' module. Processes 'text' feature. """

    stop_words = nltk.corpus.stopwords.words(['english'])
    lem = WordNetLemmatizer()

    def cleaning(data):
        # remove urls
        tweet_without_url = re.sub(r'http\S+',' ', data)

        # remove hashtags
        tweet_without_hashtag = re.sub(r'#\w+', ' ', tweet_without_url)

        # Remove mentions and characters that not in the English alphabets
        tweet_without_mentions = re.sub(r'@\w+',' ', tweet_without_hashtag)
        precleaned_tweet = re.sub('[^A-Za-z]+', ' ', tweet_without_mentions)

        # Tokenize
        tweet_tokens = TweetTokenizer().tokenize(precleaned_tweet)

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


def textblob_processing(df, last_date):
    """
    Applies TextBlob sentiment analisys to 'cleaned_tweets' feature in the DataFrame df
    """
    df = clean_text1(df)
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
    df = fill_gap(df, last_date)
    df['unix'] = df.date.apply(timestamp_2_time)

    df["date"] = df["date"].astype(str)

    return df
