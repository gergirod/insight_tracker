import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import jwt
from insight_tracker.db import create_user_if_not_exists, get_user_company_info
from datetime import datetime, timedelta
import extra_streamlit_components as stx
import logging
import time

logging.basicConfig(filename='auth.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Auth0 configuration
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")
# Initialize OAuth2 session with Auth0
auth0 = OAuth2Session(
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    scope="openid profile email offline_access",
    redirect_uri=AUTH0_CALLBACK_URL
)

# Initialize cookie manager at module level without caching
cookie_manager = stx.CookieManager()

# Add at the top of the file
_last_auth_attempt = 0
MIN_AUTH_INTERVAL = 0.5  # Reduce from 2 to 0.5 seconds

def save_auth_cookie(token, expiry_days=7):
    """
    Save authentication token to cookies
    
    Args:
        token (str): The authentication token to save
        expiry_days (int): Number of days until cookie expires
    """
    try:
        cookie_manager.set("auth_token", token, 
                          expires_at=datetime.now() + timedelta(days=expiry_days),
                          key='save_auth_token')
        return True
    except Exception as e:
        logging.error(f"Error saving auth cookie: {e}")
        return False

def get_auth_cookie():
    """
    Retrieve authentication token from cookies
    
    Returns:
        str: The authentication token if found, None otherwise
    """
    try:
        return cookie_manager.get('auth_token')
    except Exception as e:
        print(f"Error retrieving auth cookie: {e}")
        return None
    
def delete_auth_cookie():
    """
    Delete authentication token from cookies
    """
    try:
        cookie_manager.delete('auth_token', key='delete_auth_token')
        return True
    except Exception as e:
        logging.error(f"Error deleting auth cookie: {e}")
        return False

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
        print(f"Error checking token expiration: {e}")
        return True

def try_silent_login():
    """Attempt silent login using stored token"""
    try:
        token = get_auth_cookie()
        if not token:
            return None
            
        if is_token_expired(token):
            cookie_manager.delete('auth_token')
            return None
            
        # If we have valid cached user info, return it
        if 'user_info' in st.session_state and st.session_state.user:
            return st.session_state.user
            
        user_info = validate_token_and_get_user(token)
        if user_info:
            st.session_state.user = user_info
            st.session_state.user_info = user_info
            return user_info
            
        return None
    except Exception as e:
        logging.error(f"Error during silent login: {e}")
        return None

def refresh_token():
    """Attempt to refresh the access token"""
    try:
        if 'refresh_token' not in st.session_state:
            return None
            
        token = auth0.refresh_token(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            refresh_token=st.session_state.refresh_token,
        )
        
        if token:
            access_token = token.get('access_token')
            id_token = token.get('id_token')
            refresh_token = token.get('refresh_token')
            
            save_auth_cookie(id_token)
            st.session_state.access_token = access_token
            st.session_state.refresh_token = refresh_token
            return access_token
            
        return None
    except Exception as e:
        logging.error(f"Error refreshing token: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def validate_token_and_get_user(token):
    try:
        user_info = auth0.get(
            f"https://{AUTH0_DOMAIN}/userinfo", 
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        
        if 'error' in user_info:
            return None
                
        return user_info
    except Exception as e:
        logging.error(f"Error validating token: {e}")
        return None

def login():
    try:
        if 'oauth_state' not in st.session_state:
            state = os.urandom(16).hex()
            st.session_state.oauth_state = state
            cookie_manager.set('oauth_state', state, 
                             expires_at=datetime.now() + timedelta(minutes=5),
                             key='set_oauth_state')
        else:
            state = st.session_state.oauth_state
        
        authorization_url, _ = auth0.create_authorization_url(
            f"https://{AUTH0_DOMAIN}/authorize",
            audience=f"https://{AUTH0_DOMAIN}/userinfo",
            state=state
        )
        
        st.markdown(f'''
        <div style="text-align: center;">
            <a href="{authorization_url}" target="_self" style="
                display: inline-block;
                background-color: #1E88E5;
                color: white;
                padding: 14px 48px;
                font-size: 16px;
                font-weight: 500;
                text-decoration: none;
                border-radius: 50px;
                border: none;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
                margin: 10px 0;
                letter-spacing: 0.3px;">
                Continue with Auth0
            </a>
        </div>
        ''', unsafe_allow_html=True)
        return False
    except Exception as e:
        logging.error(f"Error in login: {str(e)}")
        return False

def signup():
    signup_url = f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid%20profile%20email&screen_hint=signup"
    
    if st.button("Sign Up with Auth0"):
        st.markdown(f'<meta http-equiv="refresh" content="0;url={signup_url}">', unsafe_allow_html=True)

def handle_callback():
    try:
        code = st.query_params['code']
        token = auth0.fetch_token(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            code=code,
            redirect_uri=AUTH0_CALLBACK_URL
        )

        access_token = token.get('access_token')
        id_token = token.get('id_token')
        
        user_info = auth0.get(
            f"https://{AUTH0_DOMAIN}/userinfo", 
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        
        # Store tokens and user info
        save_auth_cookie(id_token)
        st.session_state.user_info = user_info
        st.session_state.user = user_info
        st.session_state.authentication_status = 'authenticated'
        
        # Create user in database
        success, is_new_user = create_user_if_not_exists(
            full_name=user_info.get('name', ''),
            email=user_info.get('email', ''),
            company="",
            role=""
        )
        st.session_state.is_new_user = is_new_user
        
        # Clear query parameters and redirect
        st.query_params.clear()
        base_url = os.getenv("BASE_URL", "/")
        st.markdown(f'<meta http-equiv="refresh" content="0;url={base_url}">', unsafe_allow_html=True)
        st.stop()

    except Exception as e:
        logging.error(f"Auth callback error: {str(e)}")
        return False

def logout():
    st.session_state.user = None
    st.session_state.authentication_status = 'unauthenticated'
    st.success("You have been logged out successfully.")
    delete_auth_cookie()
    st.rerun()

def clear_auth_cache():
    """Clear all authentication-related cache and state"""
    try:
        # Clear session state
        keys_to_clear = [
            'user_info', 
            'auth_attempt_count',
            'rate_limited',
            'last_auth_check',
            'access_token',
            'refresh_token'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Clear cookie
        delete_auth_cookie()
        
        # Clear cache
        validate_token_and_get_user.clear()
        return True
    except Exception as e:
        logging.error(f"Error clearing auth cache: {e}")
        return False

def cleanup_auth_state():
    """Clean up authentication state"""
    if 'oauth_state' in st.session_state:
        del st.session_state.oauth_state
    cookie_manager.delete('oauth_state', key='cleanup_oauth_state')