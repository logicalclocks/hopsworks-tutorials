import hopsworks
import streamlit as st
import plotly.express as px
from matplotlib import pyplot

import pandas as pd
import numpy as np
import warnings


warnings.filterwarnings("ignore")


def print_fancy_header(text, font_size=22, color="#ff5f27"):
    res = f'<span style="color:{color}; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )


progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.title('Fraud transactions detection')

st.write(36 * "-")
print_fancy_header('\n📡 Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()

progress_bar.progress(35)


@st.cache_resource()
def retrive_dataset():
    st.write(36 * "-")
    trans_fg = fs.get_feature_group('transactions_fraud_online_fg', version=1)
    cc_nums = trans_fg.show(5).cc_num.tolist()
    print_fancy_header('\n💾 Dataset Retrieving...')
    feature_view = fs.get_feature_view("transactions_fraud_online_fv", 1)
    X_train, X_test, y_train, y_test = feature_view.get_train_test_split(1)

    return feature_view, X_train, X_test, y_train, y_test, cc_nums


feature_view, X_train, X_test, y_train, y_test, cc_nums = retrive_dataset()
# show concatenated training dataset (label is a 'fraud_label' feature)
st.dataframe(pd.concat([X_test.head(),(y_test.head())], axis=1))
progress_bar.progress(55)

def explore_data():
    st.write(36 * "-")
    print_fancy_header('\n👁 Data Exploration...')
    labels = ["Normal", "Fraudulent"]
    unique, counts = np.unique(y_train.fraud_label.values, return_counts=True)
    values = counts.tolist()

    def plot_pie(values, labels):
        fig = px.pie(values=values, names=labels, title='Distribution of fraud transactions')
        return fig

    fig1 = plot_pie(values, labels)
    st.plotly_chart(fig1)
    progress_bar.progress(70)


explore_data()


st.write(36 * "-")
print_fancy_header('\n🤖 Connecting to Model Registry on Hopsworks...')
@st.cache()
def get_deployment(project):
    ms = project.get_model_serving()
    deployment = ms.get_deployment("fraudonlinemodeldeployment")
    deployment.start(await_running=180)
    return deployment

deployment = get_deployment(project)

progress_bar.progress(85)

st.write(36 * "-")
print_fancy_header('\n🧠 Interactive predictions...')
with st.form(key="Selecting cc_num"):
    option = st.selectbox(
         'Select a credit card to get a fraud analysis.',
         cc_nums,
         )
    submit_button = st.form_submit_button(label='Submit')
if submit_button:
    st.write('You selected:', option)
    res = deployment.predict(inputs=[int(option)])
    negative = "**👌 Not a suspicious**"
    positive = "**🆘 Fraudulent**"
    res = negative if res["predictions"][0] == -1 else positive
    st.write(res, "transaction.")
    progress_bar.progress(100)
    st.write(36 * "-")

    print_fancy_header('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
