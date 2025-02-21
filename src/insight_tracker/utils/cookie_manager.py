import streamlit as st
import time
import logging
import extra_streamlit_components as stx
import jwt
from datetime import datetime, timedelta
import json

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
    logger.info("Storing auth cookies")
    try:
        if access_token:
            cookie_manager = get_cookie_manager()
            
            # Store tokens as a single JSON object
            tokens = {
                "access_token": access_token,
                "id_token": id_token if id_token else ""
            }
            
            # Store as a single cookie
            cookie_manager.set("auth_tokens", json.dumps(tokens))
            logger.info("Auth tokens stored in cookie")
            
            # Verify the cookie was set
            stored_tokens = cookie_manager.get("auth_tokens")
            if stored_tokens:
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
        logger.error(f"Access token length: {len(access_token) if access_token else 0}")
        return False

def load_auth_cookie():
    """Load authentication data from browser cookies"""
    try:
        cookie_manager = get_cookie_manager()
        stored_tokens = cookie_manager.get("auth_tokens")
        
        logger.info("Checking auth cookie")
        if not stored_tokens:
            logger.info("No auth cookie found")
            return False
            
        # Parse stored tokens
        tokens = json.loads(stored_tokens)
        access_token = tokens.get("access_token")
        id_token = tokens.get("id_token")
        
        logger.info(f"Found tokens - Access: {bool(access_token)}, ID: {bool(id_token)}")
        
        if not access_token or not id_token:
            logger.info("Missing required tokens")
            return False
            
        # Check if token is expired
        if is_token_expired(id_token):
            logger.info("ID token is expired, clearing")
            clear_auth_cookie()
            return False
            
        logger.info("Tokens are valid and not expired")
        st.session_state.access_token = access_token
        st.session_state.id_token = id_token
        return True
        
    except Exception as e:
        logger.error(f"Error loading auth cookie: {e}")
        return False

def clear_auth_cookie():
    """Clear authentication data from cookies"""
    logger.info("Clearing auth cookie")
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete("auth_tokens")
        if 'access_token' in st.session_state:
            del st.session_state.access_token
        if 'id_token' in st.session_state:
            del st.session_state.id_token
        logger.info("Auth cookie cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing auth cookie: {e}")

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