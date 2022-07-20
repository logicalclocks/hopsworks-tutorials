import datetime
import pandas as pd
import tweepy
import os #provides ways to access the Operating System and allows us to read the environment variables

from settings import LOCALLY


if LOCALLY:
    from dotenv import load_dotenv
    load_dotenv()


def get_api():
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")

    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        # Check for env variables in Heroku
#     print(TWITTER_API_KEY, "- TWITTER_API_KEY")
#     print(BINANCE_API_KEY, "- BINANCE_API_KEY")

    authentificate = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    authentificate.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(authentificate, wait_on_rate_limit=True)

    return api


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
