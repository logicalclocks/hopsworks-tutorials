import streamlit as st
import hopsworks
import joblib
from openai import OpenAI
from functions.llm_chain import (
    load_model, 
    get_llm_chain, 
    generate_response, 
    generate_response_openai,
)
import warnings
warnings.filterwarnings('ignore')

st.title("🌤️ AirQuality AI assistant 💬")

@st.cache_resource()
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


@st.cache_resource()
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

# Initialize or clear chat messages based on response source change
if "response_source" not in st.session_state or "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.response_source = ""

# User choice for model selection in the sidebar with OpenAI API as the default
new_response_source = st.sidebar.radio(
    "Choose the response generation method:",
    ('Hermes LLM', 'OpenAI API'),
    index=1  # Sets "OpenAI API" as the default selection
)

# If the user switches the response generation method, clear the chat
if new_response_source != st.session_state.response_source:
    st.session_state.messages = []  # Clear previous chat messages
    st.session_state.response_source = new_response_source  # Update response source in session state

    # Display a message indicating chat was cleared (optional)
    st.experimental_rerun()  # Rerun the app to reflect changes immediately
    
    
if new_response_source == 'OpenAI API':
    openai_api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
    if openai_api_key:
        client = OpenAI(
            api_key=openai_api_key
        )
        st.sidebar.success("API key saved successfully ✅")
        
elif new_response_source == 'Hermes LLM':
    # Conditionally load the LLM, tokenizer, and llm_chain if Local Model is selected
    model_llm, tokenizer, llm_chain = retrieve_llm_chain()

    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_query := st.chat_input("How can I help you?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_query)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    st.write('⚙️ Generating Response...')

    if new_response_source == 'Hermes LLM':
        # Generate a response to the user query
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
        
    elif new_response_source == 'OpenAI API' and openai_api_key:
        response = generate_response_openai(   
            user_query,
            feature_view,
            model_air_quality,
            encoder,
            client,
            verbose=False,
        )
        
    else:
        response = "Please select a response generation method and provide necessary details."

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    