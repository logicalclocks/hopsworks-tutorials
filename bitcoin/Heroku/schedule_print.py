import hopsworks
from datetime import datetime
from btc_data_parsing import parse_btc_data
from btc_data_processing import process_btc_data
from tweets_parsing import get_last_tweets
from tweets_processing import textblob_processing, vader_processing

import schedule, time
import os #provides ways to access the Operating System and allows us to read the environment variables

from settings import LOCALLY, PROCESS_TWEETS, USE_FEATURE_STORE


if LOCALLY:
    from dotenv import load_dotenv
    load_dotenv()

def job():
    print("#" * 12)
    print("STARTING")
    print("#" * 12)

    if USE_FEATURE_STORE:

        project = hopsworks.login()

        fs = project.get_feature_store()
        
        print("Connected to the FS.", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    btc_data = parse_btc_data() # TODO: for how many previous days?

    print("#" * 12)
    print('Parsed BTC timeseries!!!', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("#" * 12)
    print("BTC dataframe shape:")
    print(btc_data.shape)

    processed_btc_data = process_btc_data(btc_data)

    print("#" * 12)
    print('Processed BTC timeseries!!!', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("#" * 12)
    print("processed BTC dataframe shape:")
    print(processed_btc_data.shape)

    if USE_FEATURE_STORE:
        btc_price_fg = fs.get_or_create_feature_group(
            name = 'btc_price_fg',
            version = 1
        )
        print('Feature Group Saved!!!', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        #btc_price_fg.insert(processed_btc_data.reset_index())

        print('Inserted!!!', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    #############################
    if PROCESS_TWEETS:
        print("#" * 12)
        print("Tweets parsing started.", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("#" * 12)

        tweets = get_last_tweets()

        print("#" * 12)
        print('Parsed tweets!!!', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("#" * 12)
        print(tweets.head(5))


        tweets_vader = vader_processing(tweets)
        tweets_textblob = textblob_processing(tweets)

        print("#" * 12)
        print('Processed tweets!!!', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("#" * 12)
        print(tweets_vader.head(5))
        print(tweets_textblob.head(5))

        if USE_FEATURE_STORE:
            tweets_textblob_fg = fs.get_or_create_feature_group(
                name = 'tweets_textblob_fg',
                version = 1,
                primary_key = ['unix'],
                online_enabled = True,
                event_time = ['unix']
            )

            tweets_vader_fg = fs.get_or_create_feature_group(
                name = 'tweets_vader_fg',
                version = 1,
                primary_key = ['unix'],
                online_enabled = True,
                event_time = ['unix']
            )

            tweets_vader_fg.insert(tweets_vader)

            tweets_textblob_fg.insert(tweets_textblob)

            print('Inserted tweets_vader_fg and tweets_textblob_fg!!!',
                  datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


    print("#" * 12)
    print('Completed!!! ')
    print("#" * 12)

schedule.every(60).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
