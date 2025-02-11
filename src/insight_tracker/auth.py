import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import jwt
from insight_tracker.db import create_user_if_not_exists, get_user_company_info
from datetime import datetime
import extra_streamlit_components as stx
import logging
from time import time

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
    scope="openid profile email",
    redirect_uri=AUTH0_CALLBACK_URL
)

# Initialize cookie manager at module level without caching
cookie_manager = stx.CookieManager()

# Add at the top of the file
_last_auth_attempt = 0
MIN_AUTH_INTERVAL = 2  # minimum seconds between auth attempts

def save_auth_cookie(token, expiry_days=1):
    """
    Save authentication token to cookies
    
    Args:
        token (str): The authentication token to save
        expiry_days (int): Number of days until cookie expires
    """
    try:
        # Save token with secure settings
        cookie_manager.set("auth_token", token)
        return True
    except Exception as e:
        print(f"Error saving auth cookie: {e}")
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
        cookie_manager.delete('auth_token')
        return True
    except Exception as e:
        print(f"Error deleting auth cookie: {e}")
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
    global _last_auth_attempt
    
    try:
        # Rate limiting check
        current_time = time()
        if current_time - _last_auth_attempt < MIN_AUTH_INTERVAL:
            logging.info("Rate limit: Skipping auth attempt")
            return None
        
        _last_auth_attempt = current_time
        
        token = get_auth_cookie()
        if not token:
            return None
            
        if is_token_expired(token):
            cookie_manager.delete('auth_token')
            return None
            
        # Only make API call if absolutely necessary
        if 'user_info' in st.session_state and st.session_state.user:
            return st.session_state.user
            
        user_info = validate_token_and_get_user(token)
        if user_info:
            st.session_state.user = user_info
            st.session_state.user_info = user_info  # Cache the user info
            return user_info
            
        return None
    except Exception as e:
        logging.error(f"Error during silent login: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def validate_token_and_get_user(token):
    try:
        if is_token_expired(token):
            return None
            
        # Check cache first
        if 'user_info' in st.session_state:
            return st.session_state.user_info
            
        user_info = auth0.get(
            f"https://{AUTH0_DOMAIN}/userinfo", 
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        
        if 'error' in user_info:
            if user_info['error'] == 'access_denied' and 'Too Many Requests' in user_info.get('error_description', ''):
                logging.warning("Rate limit hit, using cached data if available")
                return st.session_state.get('user_info')
        
        st.session_state.user_info = user_info
        return user_info
    except Exception as e:
        logging.error(f"Error validating token: {e}")
        return None

def login():
    authorization_url, _ = auth0.create_authorization_url(
        f"https://{AUTH0_DOMAIN}/authorize",
        audience=f"https://{AUTH0_DOMAIN}/userinfo",
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
        <div style="
            margin-top: 8px;
            font-size: 13px;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="#666">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
            </svg>
            Secure authentication powered by Auth0
        </div>
    </div>
    ''', unsafe_allow_html=True)
    return False

def signup():
    signup_url = f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid%20profile%20email&screen_hint=signup"
    
    if st.button("Sign Up with Auth0"):
        st.markdown(f'<meta http-equiv="refresh" content="0;url={signup_url}">', unsafe_allow_html=True)

def handle_callback():
    query_params = st.query_params

    print(f"Query params: {query_params}")

    if 'code' not in query_params:
        print("Authorization code not found.")
        return False

    try:
        code = query_params['code']
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
        
        # Create or update user in database
        success, is_new_user = create_user_if_not_exists(
            full_name=user_info.get('name', ''),
            email=user_info.get('email', ''),
            company="",  # Empty initially
            role=""      # Empty initially
        )

        save_auth_cookie(id_token)
        st.session_state.is_new_user = is_new_user
        st.session_state.user = user_info
        st.session_state.authentication_status = 'authenticated'
        
        # Clear query parameters and redirect to base URL
        st.query_params.clear()
        base_url = os.getenv("BASE_URL", "/")
        st.markdown(f'<meta http-equiv="refresh" content="0;url={base_url}">', unsafe_allow_html=True)
        st.stop()

    except Exception as e:
        print(f"Error during callback handling: {e}")
        logging.error(f"Auth callback error: {str(e)}")
        return False

def logout():
    st.session_state.user = None
    st.session_state.authentication_status = 'unauthenticated'
    st.success("You have been logged out successfully.")
    delete_auth_cookie()
    st.rerun()