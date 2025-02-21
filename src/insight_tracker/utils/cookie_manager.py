import streamlit as st
import time
import logging

logger = logging.getLogger(__name__)

def store_auth_cookie(access_token):
    """Store authentication data in session state"""
    logger.debug("Storing auth cookie")
    if access_token:
        st.session_state.access_token = access_token
        st.session_state.token_expiry = time.time() + 3600  # 1 hour expiry
        logger.debug(f"Cookie stored with expiry: {st.session_state.token_expiry}")

def load_auth_cookie():
    """Load authentication data from session state"""
    access_token = st.session_state.get('access_token')
    token_expiry = st.session_state.get('token_expiry', 0)
    
    logger.debug(f"Loading auth cookie - Token exists: {bool(access_token)}, Expiry: {token_expiry}")
    
    if access_token and time.time() < token_expiry:
        logger.debug("Cookie is valid")
        return True
    
    # Clear expired token
    if access_token:
        logger.debug("Cookie expired, clearing")
        clear_auth_cookie()
    return False

def clear_auth_cookie():
    """Clear authentication data from session state"""
    if 'access_token' in st.session_state:
        del st.session_state.access_token
    if 'token_expiry' in st.session_state:
        del st.session_state.token_expiry 