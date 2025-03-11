import time
from datetime import datetime
import streamlit as st

from functions.interaction_tracker import get_tracker
from functions.utils import (
    print_header, fetch_and_process_image, process_description, 
    get_item_image_url
)


def display_item(item_id, score, articles_fv, customer_id, tracker, source, fg_updater):
    """Display a single item with its interactions"""
    image_url = get_item_image_url(item_id, articles_fv)
    img = fetch_and_process_image(image_url)
    
    if img:
        st.image(img, use_column_width=True)
        st.write(f"**🎯 Score:** {score:.4f}")
        
        # View Details button
        details_key = f'{source}_details_{item_id}'
        if st.button("📝 View Details", key=details_key):
            tracker.track(customer_id, item_id, 'click')
            with st.expander("Item Details", expanded=True):
                description = process_description(articles_fv.get_feature_vector({'article_id': item_id})[-2])
                st.write(description)
        
        # Buy button
        buy_key = f'{source}_buy_{item_id}'
        if st.button("🛒 Buy", key=buy_key):
            # Track interaction
            tracker.track(customer_id, item_id, 'purchase')
            
            # Insert transaction
            purchase_data = {
                'customer_id': customer_id,
                'article_id': item_id
            }
            
            if fg_updater.insert_transaction(purchase_data):
                st.success(f"✅ Item {item_id} purchased!")
                st.experimental_rerun()
            else:
                st.error("Failed to record transaction, but purchase was tracked")

def customer_recommendations(articles_fv, recommender_deployment, customer_id, tracker, fg_updater):
    """Handle customer-based recommendations"""    
    # Initialize or update recommendations
    if 'customer_recs' not in st.session_state:
        st.session_state.customer_recs = []
        st.session_state.prediction_time = None
        
    # Only get new predictions if:
    # 1. Button is clicked OR
    # 2. No recommendations exist OR
    # 3. Customer ID changed
    if (st.sidebar.button('Get Recommendations', key='get_recommendations_button') or 
        not st.session_state.customer_recs or 
        'last_customer_id' not in st.session_state or 
        st.session_state.last_customer_id != customer_id):
        
        with st.spinner('🔮 Getting recommendations...'):
            # Format timestamp with milliseconds
            current_time = datetime.now()
            formatted_timestamp = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
            
            st.session_state.prediction_time = formatted_timestamp
            st.session_state.last_customer_id = customer_id
            
            # Get predictions from model
            deployment_input = [
                {
                    "customer_id": customer_id,
                    "transaction_date": formatted_timestamp,
                }
            ]
            
            prediction = recommender_deployment.predict(inputs=deployment_input)['predictions']['ranking']
            
            # Filter out purchased items
            available_items = [
                (item_id, score) for score, item_id in prediction 
                if tracker.should_show_item(customer_id, item_id)
            ]
            
            # Store recommendations and extras
            st.session_state.customer_recs = available_items[:12]
            st.session_state.extra_recs = available_items[12:]
            
            # Track shown items
            tracker.track_shown_items(
                customer_id, 
                [(item_id, score) for item_id, score in st.session_state.customer_recs]
            )
            
            st.sidebar.success("✅ Got new recommendations")
    
    # Display recommendations
    print_header('📝 Top 12 Recommendations:')
    
    if not st.session_state.customer_recs:
        st.warning("No recommendations available. Click 'Get Recommendations' to start.")
        return
        
    # Display items in 3x4 grid
    for row in range(3):
        cols = st.columns(4)
        for col in range(4):
            idx = row * 4 + col
            if idx < len(st.session_state.customer_recs):
                item_id, score = st.session_state.customer_recs[idx]
                if tracker.should_show_item(customer_id, item_id):
                    with cols[col]:
                        display_item(item_id, score, articles_fv, customer_id, tracker, 'customer', fg_updater)
                else:
                    # Replace purchased item with one from extras
                    if st.session_state.extra_recs:
                        new_item = st.session_state.extra_recs.pop(0)
                        st.session_state.customer_recs.append(new_item)
                    st.session_state.customer_recs.pop(idx)
                    st.experimental_rerun()