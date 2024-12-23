import streamlit as st
from datetime import datetime
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .utils import (
    print_header, fetch_and_process_image, process_description, 
    get_item_image_url
)
from .interaction_tracker import get_tracker
from .feature_group_updater import get_fg_updater


def initialize_llm_state():
    """Initialize all necessary session state variables for LLM recommendations"""
    if 'llm_recommendations' not in st.session_state:
        st.session_state.llm_recommendations = []
    if 'outfit_summary' not in st.session_state:
        st.session_state.outfit_summary = ""
    if 'llm_extra_items' not in st.session_state:
        st.session_state.llm_extra_items = {}

        
def display_item(item_id, score, articles_fv, customer_id, tracker, source):
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
            fg_updater = get_fg_updater()
            purchase_data = {
                'customer_id': customer_id,
                'article_id': item_id
            }
            
            if fg_updater.insert_transaction(purchase_data):
                st.success(f"✅ Item {item_id} purchased!")
                st.experimental_rerun()
            else:
                st.error("Failed to record transaction, but purchase was tracked")

def customer_recommendations(articles_fv, ranking_deployment, query_model_deployment, customer_id):
    """Handle customer-based recommendations"""
    tracker = get_tracker()
    
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
            # Format timestamp with microseconds
            current_time = datetime.now()
            formatted_timestamp = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
            
            st.session_state.prediction_time = formatted_timestamp
            st.session_state.last_customer_id = customer_id
            
            # Get predictions from model
            deployment_input = {
                "instances": {
                    "customer_id": customer_id,
                    "transaction_date": formatted_timestamp,
                }
            }
            
            prediction = query_model_deployment.predict(deployment_input)['predictions']['ranking']
            
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
                        display_item(item_id, score, articles_fv, customer_id, tracker, 'customer')
                else:
                    # Replace purchased item with one from extras
                    if st.session_state.extra_recs:
                        new_item = st.session_state.extra_recs.pop(0)
                        st.session_state.customer_recs.append(new_item)
                    st.session_state.customer_recs.pop(idx)
                    st.experimental_rerun()


def get_fashion_chain(api_key):
    model = ChatOpenAI(
        model_name='gpt-4o-mini-2024-07-18',
        temperature=0.7,
        openai_api_key=api_key,
    )
    template = """
    You are a fashion recommender for H&M. 
    
    Customer request: {user_input}
    
    Gender: {gender}
    
    Generate 3-5 necessary fashion items with detailed descriptions, tailored for an H&M-style dataset and appropriate for the specified gender. 
    Each item description should be specific, suitable for creating embeddings, and relevant to the gender. 
    
    STRICTLY FOLLOW the next response format:
    <emoji> <item 1 category> @ <item 1 description> | <emoji> <item 2 category> @ <item 2 description> | <emoji> <item 3 category> @ <item 3 description> | <Additional items if necessary> | <BRIEF OUTFIT SUMMARY AND STYLING TIPS WITH EMOJIS>
    
    Example for male gender:
    👖 Pants @ Slim-fit dark wash jeans with subtle distressing | 👕 Top @ Classic white cotton polo shirt with embroidered logo | 👟 Footwear @ Navy canvas sneakers with white soles | 🧥 Outerwear @ Lightweight olive green bomber jacket | 🕶️👔 Versatile casual look! Mix and match for various occasions. Add accessories for personal flair! 💼⌚
    
    Example for female gender:
    👗 Dress @ Floral print wrap dress with flutter sleeves | 👠 Footwear @ Strappy nude block heel sandals | 👜 Accessory @ Woven straw tote bag with leather handles | 🧥 Outerwear @ Cropped denim jacket with raw hem | 🌸👒 Perfect for a summer day out! Layer with the jacket for cooler evenings. Add a wide-brim hat for extra style! 💃🏻🕶️
    
    Ensure each item category has a relevant emoji, each item description is detailed, unique, and appropriate for the specified gender. 
    Make sure to take into account the gender when selecting items and descriptions. 
    The final section should provide a brief summary and styling tips with relevant emojis. Tailor your recommendations to the specified gender.
    """
    prompt = PromptTemplate(
        input_variables=["user_input", "gender"],
        template=template,
    )
    fashion_chain = LLMChain(
        llm=model,
        prompt=prompt,
        verbose=True
    )
    return fashion_chain


def get_fashion_recommendations(user_input, fashion_chain, gender):
    """Get recommendations from the LLM"""
    response = fashion_chain.run(user_input=user_input, gender=gender)
    items = response.strip().split(" | ")
    
    outfit_summary = items[-1] if len(items) > 1 else "No summary available."
    item_descriptions = items[:-1] if len(items) > 1 else items
    
    parsed_items = []
    for item in item_descriptions:
        try:
            emoji_category, description = item.split(" @ ", 1)
            emoji, category = emoji_category.split(" ", 1)
            parsed_items.append((emoji, category, description))
        except ValueError:
            parsed_items.append(("🔷", "Item", item))
    
    return parsed_items, outfit_summary


def display_llm_item(item_data, col, articles_fv, customer_id, tracker):
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
        fg_updater = get_fg_updater()
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
    
    
def display_category_items(emoji, category, items, articles_fv, customer_id, tracker):
    """Display items for a category and handle purchases"""
    st.markdown(f"## {emoji} {category}")
    
    if items:
        st.write(f"**Recommendation: {items[0][0]}**")
        
        # Calculate number of rows needed
        items_per_row = 5
        num_rows = (len(items) + items_per_row - 1) // items_per_row
        
        need_rerun = False
        remaining_items = []
        
        # Display items row by row
        for row in range(num_rows):
            start_idx = row * items_per_row
            end_idx = min(start_idx + items_per_row, len(items))
            row_items = items[start_idx:end_idx]
            
            cols = st.columns(items_per_row)
            
            for idx, item_data in enumerate(row_items):
                if tracker.should_show_item(customer_id, item_data[1][0]):
                    with cols[idx]:
                        if display_llm_item(item_data, cols[idx], articles_fv, customer_id, tracker):
                            need_rerun = True
                        else:
                            remaining_items.append(item_data)
                            
        st.markdown("---")
        return need_rerun, remaining_items
    return False, []


def llm_recommendations(articles_fv, api_key, customer_id):
    """Handle LLM-based recommendations with proper state management"""
    st.write("🤖 LLM Fashion Recommender")
    
    # Initialize session state
    initialize_llm_state()
    
    tracker = get_tracker()
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
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
                fashion_chain = get_fashion_chain(api_key)
                item_recommendations, summary = get_fashion_recommendations(
                    user_request, fashion_chain, gender
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
                    was_purchased = display_llm_item(item_data, cols[idx % n_cols], articles_fv, customer_id, tracker)
                    
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
