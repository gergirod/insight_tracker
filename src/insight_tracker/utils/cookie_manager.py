import streamlit as st
import time
import logging
import extra_streamlit_components as stx
import jwt
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize cookie manager
cookie_manager = stx.CookieManager()

def store_auth_cookie(access_token):
    """Store authentication data in browser cookies"""
    logger.info("Storing new auth cookie")
    try:
        if access_token:
            # Save token with secure settings
            cookie_manager.set("auth_token", access_token)
            logger.info("Cookie stored successfully")
            logger.info(f"Current cookies: {cookie_manager.get_all()}")
        else:
            logger.warning("Attempted to store empty access token")
    except Exception as e:
        logger.error(f"Error storing cookie: {e}")

def load_auth_cookie():
    """Load authentication data from browser cookies"""
    try:
        token = cookie_manager.get('auth_token')
        logger.info("Checking auth cookie:")
        logger.info(f"Token exists: {bool(token)}")
        
        if not token:
            logger.info("No cookie found")
            return False
            
        # Check if token is expired
        if is_token_expired(token):
            logger.info("Cookie found but expired, clearing")
            clear_auth_cookie()
            return False
            
        logger.info("Cookie is valid and not expired")
        st.session_state.access_token = token  # Store in session state for convenience
        return True
        
    except Exception as e:
        logger.error(f"Error loading cookie: {e}")
        return False

def clear_auth_cookie():
    """Clear authentication data from cookies"""
    logger.info("Clearing auth cookie")
    try:
        cookie_manager.delete('auth_token')
        if 'access_token' in st.session_state:
            del st.session_state.access_token
        logger.info("Cookie cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing cookie: {e}")

def is_token_expired(token):
    """Check if the token is expired"""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = decoded.get('exp')
        if not exp_timestamp:
            return True

        # Add some buffer (5 minutes) to prevent edge cases
        current_timestamp = datetime.now().timestamp() - 300
        return exp_timestamp < current_timestamp
    except Exception as e:
        logger.error(f"Error checking token expiration: {e}")
        return True 