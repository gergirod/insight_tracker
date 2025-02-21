import streamlit as st
import time
import logging
import extra_streamlit_components as stx
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@st.cache_resource(show_spinner=False)
def get_cookie_manager():
    """Get or create cookie manager in the Streamlit context"""
    return stx.CookieManager()

def store_auth_cookie(access_token):
    """Store authentication data in browser cookies"""
    logger.info("Storing new auth cookie")
    try:
        if access_token:
            cookie_manager = get_cookie_manager()
            
            # Generate a unique key for this cookie
            cookie_key = "auth_token_" + str(int(time.time()))
            
            # Set the cookie
            cookie_manager.set(cookie_key, access_token)
            logger.info(f"Cookie set with key: {cookie_key}")
            
            # Store the key in session state
            st.session_state.auth_cookie_key = cookie_key
            st.session_state.token_expiry = int((datetime.now() + timedelta(days=7)).timestamp())
            
            # Verify the cookie was set
            stored_token = cookie_manager.get(cookie_key)
            if stored_token == access_token:
                logger.info("Cookie verified as stored successfully")
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
        cookie_key = st.session_state.get('auth_cookie_key')
        
        if not cookie_key:
            logger.info("No cookie key found in session state")
            return False
            
        token = cookie_manager.get(cookie_key)
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
        st.session_state.access_token = token
        return True
        
    except Exception as e:
        logger.error(f"Error loading cookie: {e}")
        return False

def clear_auth_cookie():
    """Clear authentication data from cookies"""
    logger.info("Clearing auth cookie")
    try:
        cookie_manager = get_cookie_manager()
        cookie_key = st.session_state.get('auth_cookie_key')
        if cookie_key:
            cookie_manager.delete(cookie_key)
            del st.session_state.auth_cookie_key
        if 'access_token' in st.session_state:
            del st.session_state.access_token
        if 'token_expiry' in st.session_state:
            del st.session_state.token_expiry
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