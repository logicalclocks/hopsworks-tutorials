import gradio as gr
import numpy as np
from PIL import Image
import hopsworks
import joblib
import os
import pandas as pd
from features import loans
import requests
import pandas as pd
import time

fv_version=1
model_version=1

start_time = time.time()

project = hopsworks.login()
fs = project.get_feature_store()

print("Login Hopsworks %s seconds ---" % (time.time() - start_time))


start_time = time.time()
mr = project.get_model_registry()
model = mr.get_model("lending_model", version=model_version)
model_dir = model.download()
model = joblib.load(model_dir + "/lending_model.pkl")

print("Download model version {}: %s seconds ---".format(model_version) % (time.time() - start_time))

start_time = time.time()

fv = fs.get_feature_view("loans_approvals", version=fv_version)

print("Initialized feature view %s seconds ---" % (time.time() - start_time))

purpose = ['vacation', 'debt_consolidation', 'credit_card','home_improvement', 'small_business', 'major_purchase', 'other',
       'medical', 'wedding', 'car', 'moving', 'house', 'educational','renewable_energy']
term = ['36 months', '60 months']


def approve_loan(id, term, purpose, zip_code, loan_amnt, int_rate):
    start_time = time.time()
    
    # On-demand feature function used to create the zip_code feature
    validated_zip_code = loans.zipcode(zip_code)
    if validated_zip_code == 0:
        raise Exception('Invalid zip code. It should have 5 digits')
    
    y_pred = 1
    
    print("Id: {}".format(id))

    arr = fv.get_feature_vector(
        {"id": id}, 
        passed_features={
            "term": term, 
            "purpose": purpose,
            "zip_code": validated_zip_code,
            "loan_amnt": loan_amnt, 
            "int_rate": int_rate
        }
    )
    print("Received Feature Vector: {}".format(arr))
 
    cols = [f.name for f in fv.schema]
    # remove the label column
    cols.remove("loan_status")
    print(cols)
    df = pd.DataFrame(data=[arr], columns=cols)
    res = model.predict(df) 


    print("Prediction time %s seconds ---" % (time.time() - start_time))    
    loan_res_url = "https://icl-blog.s3.ap-southeast-1.amazonaws.com/uploads/2015/01/loan_approved.jpg"
    if res[0] == 0:
        loan_res_url = "https://elevatecredit.africa/wp-content/uploads/2022/03/download-2.jpg"
    img = Image.open(requests.get(loan_res_url, stream=True).raw)            
    return img

demo = gr.Interface(
    fn=approve_loan,
    title="Loan Approval",
    description="Enter your details to see if your loan will be approved or not.",
    allow_flagging="never",
    inputs=[
        gr.Number(label="id"),
        gr.Dropdown(term, label="term"),
        gr.Dropdown(purpose, label="purpose"),
        gr.Number(label="zip_code"),
        gr.Number(label="loan_amnt"),
        gr.Number(label="int_rate"),
        ],
    examples=[
        [111, "36 months","home_improvement", 45725, 5000, 4.5],
    ],
    outputs=gr.Image(type="pil"))

demo.launch()

