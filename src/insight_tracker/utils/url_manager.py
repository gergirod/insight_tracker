import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://insight-tracker.com")

def redirect_to_base_url():
    """Redirect to base URL using JavaScript"""
    js_code = f"""
        <script>
            window.location.href = "{BASE_URL}";
        </script>
    """
    st.markdown(js_code, unsafe_allow_html=True) 