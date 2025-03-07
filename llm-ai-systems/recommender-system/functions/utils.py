import streamlit as st
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import re
import hopsworks

def print_header(text, font_size=22):
    res = f'<span style="font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True)

@st.cache_data(ttl=900)
def fetch_and_process_image(image_url, width=200, height=300):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((width, height), Image.LANCZOS)
        return img
    except (UnidentifiedImageError, requests.RequestException, IOError):
        return None

def process_description(description):
    details_match = re.search(r'Details: (.+?)(?:\n|$)', description)
    return details_match.group(1) if details_match else "No details available."

def get_item_image_url(item_id, articles_fv):
    return articles_fv.get_feature_vector({'article_id': item_id})[-1]
