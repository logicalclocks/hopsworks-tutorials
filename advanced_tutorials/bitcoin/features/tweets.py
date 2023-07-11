import os
import re
import datetime
import inspect
import pandas as pd
from textblob import TextBlob
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from dotenv import load_dotenv
load_dotenv()

import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

import warnings
warnings.filterwarnings('ignore')


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
    
    try:
        api = get_api()
    except TypeError:
        print("Invalid Twitter API keys! Please check the .env file with API keys, that is located inside this project folder.")
        return None

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
    df['unix'] = df.date.apply(convert_date_to_unix)

    return df


def vader_processing(df_input):
    """
    Takes a DataFrame with 'text' column (cleaned using 'clean_text1' function) and
    returns a DataFrame with VADER-analized score.
    """
    df = df_input.copy()
    analyzer = SentimentIntensityAnalyzer()
    compound = []
    for s in df['text']:
        vs = analyzer.polarity_scores(str(s))
        compound.append(vs["compound"])
    df["compound"] = compound
    df.date = pd.to_datetime(df.date)
    df = df.set_index("date")[["compound"]]
    df = df.resample('1D').sum()
    df = df.reset_index()
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['unix'] = df.date.apply(convert_date_to_unix)

    return df


def decode_features(df, feature_view, training_dataset_version=1):
    """Decodes features using corresponding transformation functions from passed Feature View object.
        !!! Columns names in passed DataFrame should be the same as column names in transformation fucntions mappers."""
    df_res = df.copy()
    
    feature_view.init_batch_scoring(training_dataset_version=1)
    td_transformation_functions = feature_view._batch_scoring_server._transformation_functions    

    res = {}
    for feature_name in td_transformation_functions:
        if feature_name in df_res.columns:
            td_transformation_function = td_transformation_functions[feature_name]
            sig, foobar_locals = inspect.signature(td_transformation_function.transformation_fn), locals()
            param_dict = dict([(param.name, param.default) for param in sig.parameters.values() if param.default != inspect._empty])
            if td_transformation_function.name == "min_max_scaler":
                df_res[feature_name] = df_res[feature_name].map(
                    lambda x: x * (param_dict["max_value"] - param_dict["min_value"]) + param_dict["min_value"])
            elif td_transformation_function.name == "standard_scaler":
                df_res[feature_name] = df_res[feature_name].map(
                    lambda x: x * param_dict['std_dev'] + param_dict["mean"])
            elif td_transformation_function.name == "label_encoder":
                dictionary = param_dict['value_to_index']
                dictionary_ = {v: k for k, v in dictionary.items()}
                df_res[feature_name] = df_res[feature_name].map(
                    lambda x: dictionary_[x])
    return df_res
