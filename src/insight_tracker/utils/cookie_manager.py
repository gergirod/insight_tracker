import streamlit as st
import time
import logging

logger = logging.getLogger(__name__)

def store_auth_cookie(access_token):
    """Store authentication data in session state"""
    logger.info("Storing new auth cookie")
    if access_token:
        expiry_time = time.time() + 3600  # 1 hour expiry
        st.session_state.access_token = access_token
        st.session_state.token_expiry = expiry_time
        logger.info(f"Cookie stored with expiry at: {expiry_time}")
        logger.info(f"Session state after storing: {dict(st.session_state)}")
    else:
        logger.warning("Attempted to store empty access token")

def load_auth_cookie():
    """Load authentication data from session state"""
    access_token = st.session_state.get('access_token')
    token_expiry = st.session_state.get('token_expiry', 0)
    current_time = time.time()
    
    logger.info("Checking auth cookie:")
    logger.info(f"Access token exists: {bool(access_token)}")
    logger.info(f"Token expiry: {token_expiry}")
    logger.info(f"Current time: {current_time}")
    logger.info(f"Time until expiry: {token_expiry - current_time} seconds")
    logger.info(f"Full session state: {dict(st.session_state)}")
    
    if access_token and current_time < token_expiry:
        logger.info("Cookie is valid and not expired")
        return True
    
    # Clear expired token
    if access_token:
        logger.info("Cookie found but expired, clearing")
        clear_auth_cookie()
    else:
        logger.info("No cookie found")
    return False

def clear_auth_cookie():
    """Clear authentication data from session state"""
    logger.info("Clearing auth cookie")
    logger.info(f"Session state before clearing: {dict(st.session_state)}")
    if 'access_token' in st.session_state:
        del st.session_state.access_token
    if 'token_expiry' in st.session_state:
        del st.session_state.token_expiry
    logger.info(f"Session state after clearing: {dict(st.session_state)}") 