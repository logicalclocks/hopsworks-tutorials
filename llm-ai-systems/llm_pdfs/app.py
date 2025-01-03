import streamlit as st
import hopsworks
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker
from functions.prompt_engineering import get_context_and_source
from functions.llm_chain import get_llm_chain
import config
import warnings
warnings.filterwarnings('ignore')

st.title("💬 AI assistant")

@st.cache_resource()
def connect_to_hopsworks():
    # Initialize Hopsworks feature store connection
    project = hopsworks.login()
    fs = project.get_feature_store()
    mr = project.get_model_registry()

    # Retrieve the 'documents' feature view
    feature_view = fs.get_feature_view(
        name="documents", 
        version=1,
    )

    # Initialize serving
    feature_view.init_serving(1)
    
    # Get the Mistral model from Model Registry
    mistral_model = mr.get_model(
        name="mistral_model",
        version=1,
    )
    
    # Download the Mistral model files to a local directory
    saved_model_dir = mistral_model.download()

    return feature_view, saved_model_dir


@st.cache_resource()
def get_models(saved_model_dir):

    # Load the Sentence Transformer
    sentence_transformer = SentenceTransformer(
        config.MODEL_SENTENCE_TRANSFORMER,
    ).to(config.DEVICE)

    llm_chain = get_llm_chain(saved_model_dir)

    return sentence_transformer, llm_chain


@st.cache_resource()
def get_reranker():
    reranker = FlagReranker(
        'BAAI/bge-reranker-large', 
        use_fp16=True,
    ) 
    return reranker


def predict(user_query, sentence_transformer, feature_view, reranker, llm_chain):
    
    st.write('⚙️ Generating Response...')
    
    session_id = {
        "configurable": {"session_id": "default"}
    }
    
    # Retrieve reranked context and source
    context, source = get_context_and_source(
        user_query, 
        sentence_transformer,
        feature_view, 
        reranker,
    )
    
    # Generate model response
    model_output = llm_chain.invoke({
            "context": context, 
            "question": user_query,
        },
        session_id,
    )

    return model_output.split('### RESPONSE:\n')[-1] + source


# Retrieve the feature view and the saved_model_dir
feature_view, saved_model_dir = connect_to_hopsworks()

# Load and retrieve the sentence_transformer and llm_chain
sentence_transformer, llm_chain = get_models(saved_model_dir)

# Retrieve the reranking model
reranker = get_reranker()

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

    response = predict(
        user_query, 
        sentence_transformer, 
        feature_view,
        reranker,
        llm_chain,
    )

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
