import streamlit as st
import hopsworks
import time
import plotly.graph_objs as go
import pandas as pd
import datetime

from btc_data_parsing import parse_btc_data
from btc_data_processing import process_btc_data
from plots import get_price_plot, get_volume_plot
from tweets_parsing import get_last_tweets
from tweets_processing import textblob_processing, vader_processing
from settings import PARSE_NEW_TWEETS


def print_fancy_header(text, font_size=24):
    res = f'<span style="color:#ff5f27; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True)


progress_bar = st.sidebar.subheader('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
model_name = st.sidebar.selectbox('🤖 Select a Model to use', ("Random Forest", "Facebook's Prophet", 'PyTorch LSTM'))
st.title('📈💰 Bitcoin Price Project 💰📈')
st.write(36 * "-")
print_fancy_header("📡 Connecting to Hopsworks Feature Store...")

project = hopsworks.login()
fs = project.get_feature_store()
progress_bar.progress(10)

st.write('\n🔮 Retrieving Geature Groups...')
btc_price_fg = fs.get_or_create_feature_group(
    name = 'btc_price_fg',
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
    name = 'tweets_textblob_fg',
    version = 1
)
tweets_vader_fg = fs.get_or_create_feature_group(
    name = 'tweets_vader_fg',
    version = 1
)

progress_bar.progress(15)

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


    progress_bar.progress(25)

    new_btc_df = parse_btc_data(last_date=last_date)
    new_btc_df.date = pd.to_datetime(new_btc_df.date)
    concat_btc_df = pd.concat([old_btc_df[new_btc_df.columns], new_btc_df]).reset_index(drop=True)

    st.write(36 * "-")
    print_fancy_header("🧮 Processing new Bitcoin timeseries data...")
    processed_btc = process_btc_data(concat_btc_df)
    processed_btc = processed_btc[processed_btc.date > str(last_date)]
    st.write("Processed BTC timeseries DataFrame:")
    st.dataframe(processed_btc.tail(5))

    progress_bar.progress(35)

    st.write(36 * "-")
    print_fancy_header("📤 Inserting new Bitcoin timeseries data into Feature Group...")
    btc_price_fg.insert(processed_btc.reset_index())

    progress_bar.progress(40)


    st.write(36 * "-")
    print_fancy_header("🎭 Processing new tweets...")
    if PARSE_NEW_TWEETS:
        st.write('\n🧙🏼‍♂️ Parsing Tweets...')
        new_tweets_df = get_last_tweets()

    elif not PARSE_NEW_TWEETS:
        new_tweets_df = pd.read_csv("tweets_example.csv", index_col=0)

    new_tweets_df.date = pd.to_datetime(new_tweets_df.date)
    st.dataframe(new_tweets_df.tail())
    progress_bar.progress(50)

    st.write(36 * "-")
    print_fancy_header("🪄 Tweets Preprocessing...")

    vader_tweets = vader_processing(new_tweets_df, last_date)
    textblob_tweets = textblob_processing(new_tweets_df, last_date)

    st.dataframe(vader_tweets.tail(5))
    st.dataframe(textblob_tweets.tail(5))
    progress_bar.progress(60)

    st.write(36 * "-")
    print_fancy_header("📤 Inserting new processed tweets data into Feature Groups...")
    tweets_vader_fg.insert(vader_tweets)
    tweets_textblob_fg.insert(textblob_tweets)

progress_bar.progress(70)


st.write(36 * "-")
print_fancy_header("🖍 Getting Feature View...")

@st.cache(suppress_st_warning=True)
def get_X():
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

    return X_train.drop(labels=["close_nextday", "unix"], axis=1)

X = get_X()
st.dataframe(X.tail(5))
progress_bar.progress(80)


st.write(36 * "-")
print_fancy_header("🤖 Using Model Deployment and making predict for tomorrow price...")
# get Hopsworks Model Serving
ms = project.get_model_serving()

# get deployment object
deployment = ms.get_deployment("btcforest")
deployment.start()
progress_bar.progress(90)

X_today = X.sort_values(by=["index"]).tail(1).values.tolist()

st.write(X_today)

data = {
    "inputs": X_today
}

res = deployment.predict(data)
prediction = res["predictions"][0]
st.subheader(f"Prediction for tomorrow, {tomorrows_date}:")
to_print = f"{round(prediction, 4)} $"
st.header(to_print)


progress_bar.progress(100)
st.write(36 * "-")
st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
deployment.stop()

st.button("Re-run")
