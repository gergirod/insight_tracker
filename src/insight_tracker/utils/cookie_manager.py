import streamlit as st
import time
import logging
import extra_streamlit_components as stx
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Global cookie manager instance
_cookie_manager = None

def get_cookie_manager():
    """Get or create cookie manager in the Streamlit context"""
    global _cookie_manager
    if _cookie_manager is None:
        _cookie_manager = stx.CookieManager()
    return _cookie_manager

def store_auth_cookie(access_token, id_token=None):
    """Store authentication data in browser cookies"""
    logger.info("Storing new auth cookie")
    try:
        if access_token:
            cookie_manager = get_cookie_manager()
            
            # Store both tokens
            cookie_manager.set("auth_token", access_token)
            if id_token:
                cookie_manager.set("id_token", id_token)
            logger.info("Cookies set successfully")
            
            # Verify the cookies were set
            stored_token = cookie_manager.get("auth_token")
            
            if stored_token == access_token:
                logger.info("Cookies verified as stored successfully")
                return True
            else:
                logger.warning("Cookie verification failed")
                return False
        else:
            logger.warning("Attempted to store empty access token")
            return False
    except Exception as e:
        logger.error(f"Error in store_auth_cookie: {e}")
        logger.error(f"Cookie value length: {len(access_token) if access_token else 0}")
        return False

def load_auth_cookie():
    """Load authentication data from browser cookies"""
    try:
        cookie_manager = get_cookie_manager()
        access_token = cookie_manager.get("auth_token")
        id_token = cookie_manager.get("id_token")
        
        logger.info("Checking auth cookies:")
        logger.info(f"Access token exists: {bool(access_token)}")
        logger.info(f"ID token exists: {bool(id_token)}")
        
        if not access_token or not id_token:
            logger.info("No cookies found")
            return False
            
        # Check if token is expired using JWT expiry
        if is_token_expired(id_token):  # Use ID token for expiry check
            logger.info("Token is expired, clearing")
            clear_auth_cookie()
            return False
            
        logger.info("Cookies are valid and token not expired")
        st.session_state.access_token = access_token
        st.session_state.id_token = id_token
        return True
        
    except Exception as e:
        logger.error(f"Error loading cookie: {e}")
        return False

def clear_auth_cookie():
    """Clear authentication data from cookies"""
    logger.info("Clearing auth cookies")
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete("auth_token")
        cookie_manager.delete("id_token")
        if 'access_token' in st.session_state:
            del st.session_state.access_token
        if 'id_token' in st.session_state:
            del st.session_state.id_token
        logger.info("Cookies cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing cookies: {e}")

def is_token_expired(token):
    """Check if the token is expired using JWT expiry"""
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