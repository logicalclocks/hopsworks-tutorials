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

import streamlit as st


progress_bar = st.sidebar.write('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.title('Fraud transactions detection')

st.text('Connecting to Hopsworks Feature Store...')
project = hopsworks.login()
fs = project.get_feature_store()
progress_bar.progress(10)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def retrive_dataset():
    st.text('--------------\n💾 Dataset Retrieving...')
    feature_view = fs.get_feature_view("transactions_fraud_online_fv", 1)
    test_mar_x, test_mar_y = feature_view.get_training_data(2) # for demonstration purposes I will retrieve
                                                               # only test data
    return feature_view, test_mar_x, test_mar_y


feature_view, test_mar_x, test_mar_y = retrive_dataset()
# show concatenated training dataset (label is a 'fraud_label' feature)
st.dataframe(pd.concat([test_mar_x.head(),(test_mar_y.head())], axis=1))
progress_bar.progress(35)



def explore_data():
    st.text('--------------\n👁 Data Exploration...')
    labels = ["Normal", "Fraudulent"]
    unique, counts = np.unique(test_mar_y.fraud_label.values, return_counts=True)
    values = counts.tolist()

    def plot_pie(values, labels):
        fig = px.pie(values=values, names=labels, title='Distribution of fraud transactions')
        return fig

    fig1 = plot_pie(values, labels)
    st.plotly_chart(fig1)
    progress_bar.progress(50)



explore_data()


def retrieve_model():
    # load model from joblib file
    return load("model.joblib")


st.text('--------------\n🧮 Retrieving Model...')
clf = retrieve_model()
progress_bar.progress(60)



@st.cache(suppress_st_warning=True)
def predict_test(clf):
    y_pred_test = clf.predict(test_mar_x)
    f_score = f1_score(test_mar_y, y_pred_test, average='micro')
    if_cm=confusion_matrix(test_mar_y, y_pred_test)
    pd.DataFrame(if_cm)
    df_cm = pd.DataFrame(if_cm, ['step', 'True Normal',  'True Fraud'], ['Pred Normal', 'step', 'Pred Fraud'])
    df_cm.drop(index="step",inplace=True)
    df_cm.drop("step", axis=1, inplace=True)

    def plot_corr_matrix(df, title):
        return px.imshow(df, text_auto=True, title=title)

    fig2 = plot_corr_matrix(df=df_cm, title="Test Predictions")
    return f_score, fig2


st.text('--------------\n〽️ Predicting test dataset and Visualizing...')
f_score, fig2 = predict_test(clf)
st.text(f"F-score: {f_score}")
st.plotly_chart(fig2)
progress_bar.progress(75)


@st.cache(suppress_st_warning=True)
def get_deployment(project):
    mr = project.get_model_registry()
    ms = project.get_model_serving()
    deployment = ms.get_deployment("fraudonlinemodeldeployment")
    deployment.start()
    return deployment


st.text('--------------\n📡 Connecting to Model Deployment on Hopsworks...')
deployment = get_deployment(project)

progress_bar.progress(85)


st.text('--------------\n🧠 Interactive predictions...')
with st.form(key="Selecting cc_num"):
    option = st.selectbox(
         'Select a credit card to get a fraud analysis.',
         (test_mar_x.cc_num.sample(5).values)
         )
    submit_button = st.form_submit_button(label='Submit')
if submit_button:
    st.write('You selected:', option)
    data = {"inputs": [str(option)]}
    res = deployment.predict(data)
    negative = "**👌 Not a suspicious**"
    positive = "**🆘 Fraudulent**"
    res = negative if res["predictions"][0] == -1 else positive
    st.write(res, "transaction.")
    deployment.stop()
    progress_bar.progress(100)
    st.text('Done ✅')
