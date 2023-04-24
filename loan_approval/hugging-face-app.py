import gradio as gr
from PIL import Image
import hopsworks

project = hopsworks.login()
fs = project.get_feature_store()

dataset_api = project.get_dataset_api()

dataset_api.download("Resources/images/confusion_matrix.png")

with gr.Blocks() as demo:
    with gr.Row():
      with gr.Column():          
          gr.Label("Confusion Maxtrix with Historical Prediction Performance for Loan Approvals")
          input_img = gr.Image("confusion_matrix.png", elem_id="confusion-matrix", shape=(800, 800))        

demo.launch()
