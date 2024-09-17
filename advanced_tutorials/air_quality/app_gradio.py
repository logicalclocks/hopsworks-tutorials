import gradio as gr
from transformers import pipeline
import numpy as np
import hopsworks
import joblib
from openai import OpenAI
from functions.llm_chain import load_model, get_llm_chain, generate_response, generate_response_openai

# Initialize the ASR pipeline
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def connect_to_hopsworks():
    # Initialize Hopsworks feature store connection
    project = hopsworks.login()
    fs = project.get_feature_store()
    
    # Retrieve the model registry
    mr = project.get_model_registry()

    # Retrieve the 'air_quality_fv' feature view
    feature_view = fs.get_feature_view(
        name="air_quality_fv", 
        version=1,
    )

    # Initialize batch scoring
    feature_view.init_batch_scoring(1)
    
    # Retrieve the 'air_quality_xgboost_model' from the model registry
    retrieved_model = mr.get_model(
        name="air_quality_xgboost_model",
        version=1,
    )

    # Download the saved model artifacts to a local directory
    saved_model_dir = retrieved_model.download()

    # Load the XGBoost regressor model and label encoder from the saved model directory
    model_air_quality = joblib.load(saved_model_dir + "/xgboost_regressor.pkl")
    encoder = joblib.load(saved_model_dir + "/label_encoder.pkl")

    return feature_view, model_air_quality, encoder


def retrieve_llm_chain():

    # Load the LLM and its corresponding tokenizer.
    model_llm, tokenizer = load_model()
    
    # Create and configure a language model chain.
    llm_chain = get_llm_chain(
        model_llm, 
        tokenizer,
    )
    
    return model_llm, tokenizer, llm_chain


# Retrieve the feature view, air quality model and encoder for the city_name column
feature_view, model_air_quality, encoder = connect_to_hopsworks()

def transcribe(audio):
    sr, y = audio
    y = y.astype(np.float32)
    if y.ndim > 1 and y.shape[1] > 1:
        y = np.mean(y, axis=1)
    y /= np.max(np.abs(y))
    return transcriber({"sampling_rate": sr, "raw": y})["text"]


# Generate query response - Adjust this function to handle both LLM and OpenAI API based on a parameter
def generate_query_response(user_query, method, openai_api_key=None):
    if method == 'Hermes LLM':
        # Load the LLM and its corresponding tokenizer and configure a language model chain
        model_llm, tokenizer, llm_chain = retrieve_llm_chain()
        
        response = generate_response(
            user_query,
            feature_view,
            model_air_quality,
            encoder,
            model_llm,
            tokenizer,
            llm_chain,
            verbose=False,
        )
        return response
    
    elif method == 'OpenAI API' and openai_api_key:
        client = OpenAI(
            api_key=openai_api_key
        )
        
        response = generate_response_openai(   
            user_query,
            feature_view,
            model_air_quality,
            encoder,
            client,
            verbose=False,
        )
        return response
        
    else:
        return "Invalid method or missing API key."

    
def handle_input(text_input=None, audio_input=None, method='Hermes LLM', openai_api_key=""):
    if audio_input is not None:
        user_query = transcribe(audio_input)
    else:
        user_query = text_input
    
    # Check if OpenAI API key is required but not provided
    if method == 'OpenAI API' and not openai_api_key.strip():
        return "OpenAI API key is required for this method."

    if user_query:
        return generate_query_response(user_query, method, openai_api_key)
    else:
        return "Please provide input either via text or voice."

    
# Setting up the Gradio Interface
iface = gr.Interface(
    fn=handle_input,
    inputs=[
        gr.Textbox(placeholder="Type here or use voice input..."), 
        gr.Audio(), 
        gr.Radio(["Hermes LLM", "OpenAI API"], label="Choose the response generation method"),
        gr.Textbox(label="Enter your OpenAI API key (only if you selected OpenAI API):", type="password")  # Removed `optional=True`
    ],
    outputs="text",
    title="🌤️ AirQuality AI Assistant 💬",
    description="Ask your questions about air quality or use your voice to interact. Select the response generation method and provide an OpenAI API key if necessary."
)

iface.launch(share=True)
