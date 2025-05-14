import streamlit as st
from sentence_transformers import SentenceTransformer

from functions.utils import (
    fetch_and_process_image, 
    process_description, 
    get_item_image_url,
)
from functions.feature_group_updater import get_fg_updater
from functions.interaction_tracker import get_tracker


def initialize_llm_state():
    """Initialize all necessary session state variables for LLM recommendations"""
    if 'llm_recommendations' not in st.session_state:
        st.session_state.llm_recommendations = []
    if 'outfit_summary' not in st.session_state:
        st.session_state.outfit_summary = ""
    if 'llm_extra_items' not in st.session_state:
        st.session_state.llm_extra_items = {}


def display_llm_item(item_data, col, articles_fv, customer_id, tracker, fg_updater):
    """Display a single LLM recommendation item and handle interactions"""
    description, item = item_data
    item_id = str(item[0])
    
    image_url = get_item_image_url(item_id, articles_fv)
    img = fetch_and_process_image(image_url)
    
    if not img:
        return False
        
    col.image(img, use_column_width=True)
    
    # View Details button
    if col.button("📝 View Details", key=f'llm_details_{item_id}'):
        tracker.track(customer_id, item_id, 'click')
        with col.expander("Item Details", expanded=True):
            col.write(process_description(item[-2]))
    
    # Buy button
    if col.button("🛒 Buy", key=f'llm_buy_{item_id}'):
        # Track interaction
        tracker.track(customer_id, item_id, 'purchase')
        
        # Insert transaction
        purchase_data = {
            'customer_id': customer_id,
            'article_id': item_id
        }
        
        if fg_updater.insert_transaction(purchase_data):
            st.success(f"✅ Item {item_id} purchased!")
            return True
        else:
            st.error("Failed to record transaction, but purchase was tracked")
    
    return False


@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')


def llm_recommendations(articles_fv, customer_id, fashion_recommender_agent, tracker, fg_updater):
    """Handle LLM-based recommendations with proper state management"""
    st.write("🤖 LLM Fashion Recommender")
    
    # Initialize session state
    initialize_llm_state()
    
    tracker = get_tracker()
    embedding_model = load_embedding_model()
    
    # Gender selection
    gender = st.selectbox(
        "Select gender:",
        ("Male", "Female")
    )
    
    # Input options
    input_options = [
        "I'm going to the beach for a week-long vacation. What items do I need?",
        "I have a formal winter wedding to attend next month. What should I wear?",
        "I'm starting a new job at a tech startup with a casual dress code. What items should I add to my wardrobe?",
        "Custom input"
    ]
    
    selected_input = st.selectbox(
        "Choose your fashion need or enter a custom one:",
        input_options
    )
    
    user_request = ""
    if selected_input == "Custom input":
        user_request = st.text_input("Enter your custom fashion need:")
    else:
        user_request = selected_input
    
    # Generate recommendations button
    if st.button("Get LLM Recommendations") and user_request:
        with st.spinner("Generating recommendations..."):
            try:
                item_recommendations, summary = fashion_recommender_agent.get_fashion_recommendations(
                    user_request, gender
                )
                
                # Clear previous recommendations
                st.session_state.llm_recommendations = []
                st.session_state.llm_extra_items = {}
                st.session_state.outfit_summary = summary
                
                for emoji, category, description in item_recommendations:
                    similar_items = get_similar_items(description, embedding_model, articles_fv)
                    shown_items = []
                    extra_items = []
                    
                    # Split items into shown and extra
                    for item in similar_items:
                        if len(shown_items) < 5 and tracker.should_show_item(customer_id, item[0]):
                            shown_items.append((description, item))
                        elif tracker.should_show_item(customer_id, item[0]):
                            extra_items.append((description, item))
                    
                    if shown_items:
                        st.session_state.llm_recommendations.append((emoji, category, shown_items))
                        st.session_state.llm_extra_items[category] = extra_items
                        
                        # Track shown items
                        tracker.track_shown_items(
                            customer_id,
                            [(item[1][0], 0.0) for item in shown_items]
                        )
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return
    
    # Display outfit summary if available
    if st.session_state.outfit_summary:
        st.markdown(f"## 🎨 Outfit Summary")
        st.markdown(f"<h3 style='font-size: 20px;'>{st.session_state.outfit_summary}</h3>", unsafe_allow_html=True)
        st.markdown("---")
    
    # Display recommendations by category
    updated_recommendations = []
    need_rerun = False
    
    for emoji, category, items in st.session_state.llm_recommendations:
        if not items:
            continue
            
        st.markdown(f"## {emoji} {category}")
        st.write(f"**Recommendation: {items[0][0]}**")
        
        # Calculate number of columns needed
        n_items = len(items)
        n_cols = min(5, n_items)
        cols = st.columns(n_cols)
        
        # Track which items to keep
        remaining_items = []
        category_updated = False
        
        # Display items
        for idx, item_data in enumerate(items):
            item_id = item_data[1][0]
            
            # Only show if not purchased
            if tracker.should_show_item(customer_id, item_id):
                with cols[idx % n_cols]:
                    # Display and handle purchase
                    was_purchased = display_llm_item(item_data, cols[idx % n_cols], articles_fv, customer_id, tracker, fg_updater)
                    
                    if was_purchased:
                        # Item was purchased, try to get replacement
                        category_updated = True
                        extra_items = st.session_state.llm_extra_items.get(category, [])
                        
                        if extra_items:
                            # Add replacement item from extras
                            new_item = extra_items.pop(0)
                            remaining_items.append(new_item)
                            st.session_state.llm_extra_items[category] = extra_items
                    else:
                        # Keep the item in display
                        remaining_items.append(item_data)
        
        # If we still have items to display in this category
        if remaining_items:
            updated_recommendations.append((emoji, category, remaining_items))
            
        if category_updated:
            need_rerun = True
            
        st.markdown("---")
    
    # Update recommendations and rerun if needed
    if need_rerun:
        st.session_state.llm_recommendations = updated_recommendations
        st.experimental_rerun()

def get_similar_items(description, embedding_model, articles_fv):
    """Get similar items based on description embedding"""
    description_embedding = embedding_model.encode(description)
    return articles_fv.find_neighbors(description_embedding, k=25)