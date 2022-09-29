import streamlit as st
import hopsworks
import time
import plotly.graph_objs as go
import pandas as pd
import datetime

from functions import *


def print_fancy_header(text, font_size=24):
    res = f'<span style="color:#ff5f27; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )


st.title('📈💰 Bitcoin Price Project 💰📈')
st.write(36 * "-")
print_fancy_header("📡 Connecting to Hopsworks Feature Store...")

project = hopsworks.login()
fs = project.get_feature_store()

st.write('\n🔮 Retrieving Geature Groups...')
btc_price_fg = fs.get_or_create_feature_group(
    name = 'bitcoin_price',
    version = 1
)

# we need previous data to make window aggregations ([7, 14, 56] days)
old_btc_df = btc_price_fg.select_all().read().sort_values(by=["date"])
st.write("Retrieved from Feature Store BTC timeseries DataFrame:")
st.dataframe(old_btc_df.tail())
st.subheader(f"There are {old_btc_df.shape[0]} records on Feature Store right now.")

fig1 = get_price_plot(old_btc_df.sort_values(by=["date"]))
fig2 = get_volume_plot(old_btc_df.sort_values(by=["date"]))

st.plotly_chart(fig1)
st.plotly_chart(fig2)

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
st.subheader(f"Last data update was on {last_date}")
today = datetime.date.today()
tomorrows_date = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
todays_date = today.strftime("%Y-%m-%d")

st.write(36 * "-")
if str(last_date) == todays_date:
    print_fancy_header("⏱ Everything is up-to-date!")
else:
    print_fancy_header("🛠 Filling the gap in our data...")
    st.write('\n🧙🏼‍♂️ Parsing BTC data...')

    new_btc_df = parse_btc_data(last_date=last_date)
    new_btc_df.date = pd.to_datetime(new_btc_df.date)
    concat_btc_df = pd.concat([old_btc_df[new_btc_df.columns], new_btc_df]).reset_index(drop=True)

    st.write(36 * "-")
    print_fancy_header("🧮 Processing new Bitcoin timeseries data...")
    processed_btc = process_btc_data(concat_btc_df)
    processed_btc = processed_btc[processed_btc.date > str(last_date)]
    st.write("Processed BTC timeseries DataFrame:")
    st.dataframe(processed_btc.tail(5))


    st.write(36 * "-")
    print_fancy_header("📤 Inserting new Bitcoin timeseries data into Feature Group...")
    btc_price_fg.insert(processed_btc)



    st.write(36 * "-")
    print_fancy_header("🎭 Processing new tweets...")
 
    st.write('\n🧙🏼‍♂️ Parsing Tweets...')
    new_tweets_df = get_last_tweets()

    # except Error as err:
    #     new_tweets_df =  pd.read_csv("https://repo.hops.works/dev/davit/bitcoin/bitcoin_tweets.csv")
    #     print("*" * 36)
    #     print("Something is wrong with your Twitter credentials. Lets use test data for now.")
    #     print(err)
    #     print("*" * 36)

    new_tweets_df.date = pd.to_datetime(new_tweets_df.date)
    st.dataframe(new_tweets_df.tail())

    st.write(36 * "-")
    print_fancy_header("🪄 Tweets Preprocessing...")

    vader_tweets = vader_processing(new_tweets_df, last_date)
    textblob_tweets = textblob_processing(new_tweets_df, last_date)

    st.dataframe(vader_tweets.tail(5))
    st.dataframe(textblob_tweets.tail(5))

    st.write(36 * "-")
    print_fancy_header("📤 Inserting new processed tweets data into Feature Groups...")
    tweets_vader_fg.insert(vader_tweets)
    tweets_textblob_fg.insert(textblob_tweets)


st.write(36 * "-")
print_fancy_header("🖍 Getting Feature View...")


@st.cache(suppress_st_warning=True)
def get_X():
    feature_view = fs.get_feature_view(
        name = 'btc_feature_view',
        version = 1
    )
    data = feature_view.query.read().sort_values('date').tail(1)
    pk_index, pk_unix = data[['index','unix']].values[0]

    vector =  feature_view.get_feature_vector(entry = {'index' : pk_index,'unix': pk_unix})
    vector.pop(1)
    vector.pop(10)

    return vector[:4] + vector[5:] + [vector[4]]


X = get_X()
st.write(X)

st.write(36 * "-")
print_fancy_header("🤖 Using Model Deployment and making predict for tomorrow price...")
# get Hopsworks Model Serving
ms = project.get_model_serving()

# get deployment object
deployment = ms.get_deployment("btcmodeldeployment")
deployment.start()

data = {
    "inputs": X
}

res = deployment.predict(data)
prediction = res["predictions"][0]
st.subheader(f"Prediction for tomorrow, {tomorrows_date}:")
to_print = f"{round(prediction, 4)} $"
st.header(to_print)

st.write(36 * "-")
st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
deployment.stop()

st.button("Re-run")
