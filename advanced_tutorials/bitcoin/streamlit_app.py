import streamlit as st
import hopsworks
import time
import plotly.graph_objs as go
import pandas as pd
import datetime

from features import bitcoin_price, tweets
from dotenv import load_dotenv

load_dotenv()


def fancy_header(text, font_size=22, color="#ff5f27"):
    res = f'<span style="color:{color}; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )


st.title('📈💰 Bitcoin Price Project 💰📈')
st.write(36 * "-")
fancy_header("📡 Connecting to the Hopsworks Feature Store...")

project = hopsworks.login()
fs = project.get_feature_store()


fancy_header(text="○ Retrieving Bitcoin Price Feature Group...",
             font_size=18, color="#00FFFF")
btc_price_fg = fs.get_or_create_feature_group(
    name = 'bitcoin_price',
    version = 1
)

# we need previous data to make window aggregations ([7, 14, 56] days)
old_btc_df = btc_price_fg.select_all().read().sort_values(by=["date"])

st.dataframe(old_btc_df.tail(3))

fig1 = bitcoin_price.get_price_plot(old_btc_df.sort_values(by=["date"]))
fig2 = bitcoin_price.get_volume_plot(old_btc_df.sort_values(by=["date"]))

st.plotly_chart(fig1)
st.plotly_chart(fig2)

fancy_header(text="○ Retrieving Tweets Feature Groups...",
             font_size=18, color="#00FFFF")
tweets_textblob_fg = fs.get_or_create_feature_group(
    name = 'bitcoin_tweets_textblob',
    version = 1
)
tweets_vader_fg = fs.get_or_create_feature_group(
    name = 'bitcoin_tweets_vader',
    version = 1
)

old_btc_df.date = pd.to_datetime(old_btc_df.date)
last_date = old_btc_df.date.max().date()
today = datetime.date.today()
tomorrows_date = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
todays_date = today.strftime("%Y-%m-%d")

st.write('Done ✅')
st.write(36 * "-")

if str(last_date) == todays_date:
    fancy_header("⏱ Everything is up-to-date!")
else:
    fancy_header("🧙🏼‍♂️ Parsing BTC data...")

    df_bitcoin_parsed = bitcoin_price.parse_btc_data(number_of_days_ago=56)

    st.write('Done ✅')
    fancy_header("🧑🏻‍🔬 Bitcoin data preprocessing...")

    df_bitcoin_processed = bitcoin_price.process_btc_data(df_bitcoin_parsed)

    st.write("Processed BTC timeseries DataFrame:")
    st.dataframe(df_bitcoin_processed.tail(3))
    fancy_header("⬆️ Inserting Bitcoin data into the Feature Group...")

    btc_price_fg.insert(df_bitcoin_processed,
                        write_options={'wait_for_job': False})

    st.write('Done ✅')
    st.write(36 * "-")
    fancy_header("🧙🏼‍♂️ Parsing Tweets...")

    df_tweets_parsed = tweets.get_last_tweets()
    df_tweets_parsed.date = pd.to_datetime(df_tweets_parsed.date)

    st.dataframe(df_tweets_parsed.tail(3))
    fancy_header("🧑🏻‍🔬 Tweets Preprocessing...")

    tweets_textblob = tweets.textblob_processing(df_tweets_parsed)
    tweets_vader = tweets.vader_processing(df_tweets_parsed)

    st.dataframe(tweets_textblob.tail(3))
    st.dataframe(tweets_vader.tail(3))
    fancy_header("⬆️ Inserting processed Tweets data into the Feature Groups...")

    tweets_vader_fg.insert(tweets_vader,
                              write_options={'wait_for_job': False})
    tweets_textblob_fg.insert(tweets_textblob,
                              write_options={'wait_for_job': False})

    st.write('Done ✅')

st.write(36 * "-")
fancy_header("🤖 Starting Model Deployment...")

ms = project.get_model_serving()
deployment = ms.get_deployment("btcmodeldeployment")
deployment.start(await_running=120)

st.write('Done ✅')
st.write(36 * "-")

fancy_header(f'🔮 Predicting price for tomorrow...')

latest_date = int(time.mktime(today.timetuple()) * 1000) # converting todays datetime to unix

data = {
    "inputs": latest_date
}

prediction = deployment.predict(data)
prediction = prediction['outputs'][0][0]
deployment.stop()
to_print = f"{round(prediction)}$ 💰"

st.header(to_print)
st.write(36 * "-")
st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
st.button("Re-run")
