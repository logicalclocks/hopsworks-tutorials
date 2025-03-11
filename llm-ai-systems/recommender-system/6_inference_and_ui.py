import os
import logging
import streamlit as st
from langchain_openai import ChatOpenAI
import hopsworks

from functions.deployment import get_deployment
from functions.two_tower_recommender_utils import customer_recommendations
from llm_recommender.agent import FashionRecommenderAgent
from llm_recommender.utils import llm_recommendations
from functions.interaction_tracker import get_tracker
from functions.feature_group_updater import get_fg_updater
from llm_assistant.inference import handle_llm_assistant_page


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CUSTOMER_IDS = [
    '5919849351d32e688f7fc0617ef3e65e0b6c5608744987dd79b72e373c32d8b1',
    '8b31e273de61b62800b633d46f071b7b2b8353f459095c5b607d4a8c537398b1',
    'aa3be689a15c58be8a969fee5ed04024756a721754eb8c0ee2886a00fe25f853',
    'b41d990c8a127dac386dd6c9f2a6ec4ac41185cd21ef2df0a952a8cbdf61ed5d',
    '55d08819b6bfff0466f4e0b25b4590edb5366dc133cf8541b7f44e7338b1ad01',
]

def initialize_page():
    """Initialize Streamlit page configuration"""
    st.set_page_config(layout="wide", initial_sidebar_state='expanded')
    st.title('👒 Fashion Items Recommender')
    st.sidebar.title("⚙️ Configuration")


@st.cache_resource()
def get_hopsworks_project():
    project = hopsworks.login()
    return project


def initialize_services():
    """Initialize tracker, updater, and deployments"""

    project = get_hopsworks_project()

    tracker = get_tracker()
    fg_updater = get_fg_updater(project)
    
    logger.info("Initializing deployments...")
    with st.sidebar:
        with st.spinner("🚀 Starting Deployments..."):
            articles_fv, recommender_deployment = get_deployment(project)
        st.success('✅ Deployments Ready')
        
        # Stop deployments button
        if st.button("⏹️ Stop Deployment", key='stop_deployments_button', type="secondary"):
            recommender_deployment.stop()
            st.success("Deployment stopped successfully!")
    
    return project, tracker, fg_updater, articles_fv, recommender_deployment


@st.cache_resource
def get_fashion_recommender_agent():
    """Create a fashion recommender agent using OpenAI's ChatGPT"""
    if 'OPENAI_API_KEY' not in os.environ:
        return None
        
    llm = ChatOpenAI(
        model_name='gpt-4o-mini-2024-07-18',
        temperature=0.7,
        api_key=os.environ['OPENAI_API_KEY'],
    )
    return FashionRecommenderAgent(llm)


def show_interaction_dashboard(tracker, fg_updater, page_selection):
    """Display interaction data and controls"""
    with st.sidebar.expander("📊 Interaction Dashboard", expanded=True):
        if page_selection in ["LLM Recommendations", "LLM Assistant"]:
            api_key = st.text_input("🔑 OpenAI API Key:", type="password", key="openai_api_key")
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                st.success("✅ API Key set successfully!")
            else:
                st.warning("⚠️ Please enter OpenAI API Key for LLM Recommendations")
            st.divider()

        interaction_data = tracker.get_interactions_data()
        
        col1, col2, col3 = st.columns(3)
        total = len(interaction_data)
        clicks = len(interaction_data[interaction_data['interaction_score'] == 1])
        purchases = len(interaction_data[interaction_data['interaction_score'] == 2])
            
        col1.metric("Total", total)
        col2.metric("Clicks", clicks)
        col3.metric("Purchases", purchases)

        st.dataframe(interaction_data, hide_index=True)
        fg_updater.process_interactions(tracker, force=True)


def handle_llm_page(articles_fv, customer_id, tracker, fg_updater):
    """Handle LLM recommendations page"""
    if 'OPENAI_API_KEY' in os.environ:
        fashion_recommender_agent = get_fashion_recommender_agent()
        if fashion_recommender_agent:
            llm_recommendations(articles_fv, customer_id, fashion_recommender_agent, tracker, fg_updater)
        else:
            st.error("Failed to initialize the LLM agent. Please check your API key.")
    else:
        st.warning("Please provide your OpenAI API Key in the Interaction Dashboard")


def process_pending_interactions(tracker, fg_updater):
    """Process interactions immediately"""
    fg_updater.process_interactions(tracker, force=True)


def main():
    # Initialize page
    initialize_page()
    
    # Initialize services
    project, tracker, fg_updater, articles_fv, recommender_deployment = initialize_services()
    
    # Select customer
    customer_id = st.sidebar.selectbox(
        '👤 Select Customer:',
        CUSTOMER_IDS,
        key='selected_customer'
    )
    
    # Page selection
    page_options = ["Customer Recommendations", "LLM Recommendations", "LLM Assistant"]
    page_selection = st.sidebar.radio("📑 Choose Page:", page_options)
    
    # Process any pending interactions with notification
    process_pending_interactions(tracker, fg_updater)
    
    # Interaction dashboard with OpenAI API key field
    show_interaction_dashboard(tracker, fg_updater, page_selection)
    
    # Handle page content
    if page_selection == "Customer Recommendations":
        customer_recommendations(articles_fv, recommender_deployment, customer_id, tracker, fg_updater)
    elif page_selection == "LLM Recommendations":
        handle_llm_page(articles_fv, customer_id, tracker, fg_updater)
    else:
        handle_llm_assistant_page(project, customer_id)

if __name__ == '__main__':
    main()