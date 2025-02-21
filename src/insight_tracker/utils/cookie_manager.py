import streamlit as st
import time
import logging
import extra_streamlit_components as stx
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_cookie_manager():
    """Get or create cookie manager in the Streamlit context"""
    if 'cookie_manager' not in st.session_state:
        cookie_manager = stx.CookieManager()
        # Initialize the cookie manager in the page
        st.markdown(cookie_manager.generate_key())
        st.session_state.cookie_manager = cookie_manager
    return st.session_state.cookie_manager

def store_auth_cookie(access_token):
    """Store authentication data in browser cookies"""
    logger.info("Storing new auth cookie")
    try:
        if access_token:
            cookie_manager = get_cookie_manager()
            # Save token with secure settings
            expiry = datetime.now() + timedelta(days=7)  # 7 days from now
            
            # First verify we can get existing cookies
            current_cookies = cookie_manager.get_all()
            logger.info(f"Existing cookies before setting: {current_cookies}")
            
            cookie_manager.set(
                "auth_token",  # key
                access_token,  # value
                expires_at=expiry  # expiry as datetime object
            )
            
            # Verify the cookie was set
            new_cookies = cookie_manager.get_all()
            logger.info(f"Cookies after setting: {new_cookies}")
            
            if 'auth_token' in new_cookies:
                logger.info("Cookie verified as stored successfully")
                return True
            else:
                logger.warning("Cookie was not stored successfully")
                return False
        else:
            logger.warning("Attempted to store empty access token")
            return False
    except Exception as e:
        logger.error(f"Error storing cookie: {e}")
        logger.error(f"Cookie value length: {len(access_token) if access_token else 0}")
        logger.error(f"Cookie expiry: {expiry}")
        return False

def load_auth_cookie():
    """Load authentication data from browser cookies"""
    try:
        cookie_manager = get_cookie_manager()
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
        cookie_manager = get_cookie_manager()
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