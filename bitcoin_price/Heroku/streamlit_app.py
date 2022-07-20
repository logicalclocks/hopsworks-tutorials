import streamlit as st
import hopsworks
import time
import plotly.graph_objs as go
import pandas as pd

from btc_data_parsing import parse_btc_data
from btc_data_processing import process_btc_data
from plots import get_price_plot, get_volume_plot
from tweets_parsing import get_last_tweets
from tweets_processing import textblob_processing, vader_processing
from settings import PARSE_NEW_TWEETS, USE_FEATURE_STORE

progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
model_name = st.sidebar.selectbox('🤖 Select a Model to use', ("Random Forest", "Facebook's Prophet", 'PyTorch LSTM'))
st.title('📈💰 Bitcoin Price Project 💰📈')
st.write(36 * "-")
st.header('\n📡 Connecting to Hopsworks Feature Store...')

if USE_FEATURE_STORE:
    project = hopsworks.login()
    fs = project.get_feature_store()
    progress_bar.progress(10)

    st.subheader('\n🔮 Retrieving Geature Groups...')
    btc_price_fg = fs.get_or_create_feature_group(
        name = 'btc_price_fg',
        version = 1
    )
    tweets_textblob_fg = fs.get_or_create_feature_group(
        name = 'tweets_textblob_fg',
        version = 1
    )
    tweets_vader_fg = fs.get_or_create_feature_group(
        name = 'tweets_vader_fg',
        version = 1
    )

    progress_bar.progress(15)


st.write(36 * "-")
st.header('\n🛠 Filling the gap in our data...')
st.subheader('\n🧙🏼‍♂️ Parsing BTC data...')
if USE_FEATURE_STORE:
    # we need previous data to make window aggregations ([7, 14, 56] days)
    old_btc_df = btc_price_fg.select_all().read()
    st.write(old_btc_df.shape)

elif not USE_FEATURE_STORE:
    old_btc_df = pd.read_csv("final_df.csv")

old_btc_df.date = pd.to_datetime(old_btc_df.date)
last_date = old_btc_df.date.max().date()
st.write("Last data update was on", last_date)
progress_bar.progress(25)

new_btc_df = parse_btc_data(last_date=last_date)
new_btc_df.date = pd.to_datetime(new_btc_df.date)
concat_btc_df = pd.concat([old_btc_df[new_btc_df.columns], new_btc_df]).reset_index(drop=True)

fig1 = get_price_plot(concat_btc_df.sort_values(by=["date"]))
st.plotly_chart(fig1)

st.write(36 * "-")
st.header('\n🧮 Processing new Bitcoin timeseries data...')
processed_btc = process_btc_data(concat_btc_df)
processed_btc = processed_btc[processed_btc.date > str(last_date)]
st.dataframe(processed_btc.tail(5))
progress_bar.progress(35)

if USE_FEATURE_STORE:
    st.write(36 * "-")
    st.header('\n📤 Inserting new Bitcoin timeseries data into Feature Group...')
    processed_btc.date = processed_btc.date.astype(str)
    btc_price_fg.insert(processed_btc.reset_index())

progress_bar.progress(40)

st.write(36 * "-")
st.header('\n🎭 Processing new tweets...')
if PARSE_NEW_TWEETS:
    st.subheader('\n🧙🏼‍♂️ Parsing Tweets...')
    new_tweets_df = get_last_tweets()

elif not PARSE_NEW_TWEETS:
    new_tweets_df = pd.read_csv("tweets_example.csv", index_col=0)

new_tweets_df.date = pd.to_datetime(new_tweets_df.date)
st.dataframe(new_tweets_df.tail())
progress_bar.progress(50)

st.write(36 * "-")
st.header('\n🪄 Tweets Preprocessing...')

vader_tweets = vader_processing(new_tweets_df, last_date)
textblob_tweets = textblob_processing(new_tweets_df, last_date)

st.dataframe(vader_tweets.tail(5))
st.dataframe(textblob_tweets.tail(5))
progress_bar.progress(60)

if USE_FEATURE_STORE:
    st.write(36 * "-")
    st.header('\n📤 Inserting new processed tweets data into Feature Groups...')
    tweets_vader_fg.insert(vader_tweets)
    tweets_textblob_fg.insert(textblob_tweets)
    progress_bar.progress(70)


st.write(36 * "-")
st.header('\n🖍 Getting Feature View...')
feature_view = fs.get_feature_view(
    name = 'btc_feature_view',
    version = 1
)

X_train, y_train = feature_view.get_training_data(
    training_dataset_version = 1
)

X_train['close'] = y_train
X_train.sort_values('unix',inplace = True)
X_train["close_nextday"] = X_train.close.shift(-1)
X_train.date = X_train.date.apply(str)
X_train.unix = X_train.unix.apply(int)
X_train.set_index('date',inplace = True)
X_train.dropna(inplace = True)

X = X_train.drop(labels=["close_nextday", "unix"], axis=1)
st.dataframe(X.tail(5))
progress_bar.progress(80)


st.write(36 * "-")
st.header('\n🤖 Using Model Deployment and making predict for tomorrow price...')
# get Hopsworks Model Serving
ms = project.get_model_serving()

# get deployment object
deployment = ms.get_deployment("btcforest")
deployment.start()
progress_bar.progress(90)

X_today = X.tail(1).values

data = {
    "inputs": X_today
}

res = deployment.predict(data)

prediction = res["predictions"][0]

st.subheader(f"Prediction for next day:\n{prediction}")

### TODO:
# functional to refit model every week, for example

progress_bar.progress(100)
st.write(36 * "-")
st.header('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
deployment.stop()

st.button("Re-run")
