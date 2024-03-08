import streamlit as st
import hopsworks
import joblib
from functions.llm_chain import load_model, get_llm_chain, generate_response
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

# Load the LLM and its corresponding tokenizer and configure a language model chain
model_llm, tokenizer, llm_chain = retrieve_llm_chain()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

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

    # Generate a response to the user query
    response = generate_response(
        user_query,
        feature_view,
        model_llm,
        tokenizer,
        model_air_quality,
        encoder,
        llm_chain,
        verbose=False,
    )

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
