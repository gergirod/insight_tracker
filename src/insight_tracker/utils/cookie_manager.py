import streamlit as st
import time

def store_auth_cookie(access_token):
    """Store authentication data in session state"""
    if access_token:
        st.session_state.access_token = access_token
        st.session_state.token_expiry = time.time() + 3600  # 1 hour expiry

def load_auth_cookie():
    """Load authentication data from session state"""
    access_token = st.session_state.get('access_token')
    token_expiry = st.session_state.get('token_expiry', 0)
    
    if access_token and time.time() < token_expiry:
        return True
    
    # Clear expired token
    if access_token:
        clear_auth_cookie()
    return False

def clear_auth_cookie():
    """Clear authentication data from session state"""
    if 'access_token' in st.session_state:
        del st.session_state.access_token
    if 'token_expiry' in st.session_state:
        del st.session_state.token_expiry 