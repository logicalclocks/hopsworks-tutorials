import streamlit as st
import hopsworks
import plotly.express as px
from matplotlib import pyplot
from joblib import dump, load

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, f1_score

import warnings


warnings.filterwarnings("ignore")


progress_bar = st.sidebar.write('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.title('Fraud transactions detection')

st.text('Connecting to Hopsworks Feature Store...')
project = hopsworks.login()
fs = project.get_feature_store()
progress_bar.progress(10)
st.text('Done ✅')

st.text('-------\n🔮 Retrieving Feature View...')
feature_view = fs.get_feature_view("transactions_fraud_online_fv", 1)
progress_bar.progress(20)
st.text('Done ✅')

st.text('-------\n💾 Dataset Retrieving...')
test_mar_x, test_mar_y = feature_view.get_training_data(2) # for demonstration purposes I will retrieve
                                                           # only test data

st.dataframe(test_mar_x.head())
st.dataframe(test_mar_y.head())

progress_bar.progress(55)

st.text('-------\n👁 Data Exploration...')
labels = ["Normal", "Fraudulent"]
unique, counts = np.unique(test_mar_y.fraud_label.values, return_counts=True)
values = counts.tolist()


def plot_pie(values, labels):
    fig = px.pie(values=values, names=labels, title='Distribution of fraud transactions')
    return fig


fig1 = plot_pie(values, labels)
st.plotly_chart(fig1)

progress_bar.progress(70)
st.text('Done ✅')


st.text('-------\n🧮 Retrieving Model...')
clf = load("model.joblib")
progress_bar.progress(80)
st.text('Done ✅')


st.text('-------\n〽️ Predicting and Evaluating...')
y_pred_test = clf.predict(test_mar_x)

st.text(f"F-score: {f1_score(test_mar_y, y_pred_test, average='micro')}")

if_cm=confusion_matrix(test_mar_y, y_pred_test)
pd.DataFrame(if_cm)
df_cm = pd.DataFrame(if_cm, ['step', 'True Normal',  'True Fraud'], ['Pred Normal', 'step', 'Pred Fraud'])
df_cm.drop(index="step",inplace=True)
df_cm.drop("step", axis=1, inplace=True)


def plot_corr_matrix(df, title):
    return px.imshow(df, text_auto=True, title=title)


fig2 = plot_corr_matrix(df=df_cm, title="Test Predictions")
st.plotly_chart(fig2)

progress_bar.progress(100)
st.text('Done ✅')
