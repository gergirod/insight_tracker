import streamlit as st
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import logging

load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL", "https://insight-tracker.com")

def redirect_to_base_url():
    """Redirect to base URL by clearing query parameters"""
    logger.info("Attempting redirect to base URL")
    logger.info(f"Current query params before redirect: {dict(st.query_params)}")
    
    # Check if we're already at base URL
    if not st.query_params:
        logger.info("Already at base URL, skipping redirect")
        return
        
    # Clear query parameters
    for key in st.query_params.keys():
        del st.query_params[key]
    
    logger.info("Redirected to base URL")
    logger.info(f"Query params after redirect: {dict(st.query_params)}")

    # Redirect to base URL using JavaScript
    js_code = f"""
        <script>
            window.location.href = "{BASE_URL}";
        </script>
    """
    st.markdown(js_code, unsafe_allow_html=True) 