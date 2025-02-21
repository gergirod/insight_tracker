import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import jwt
from insight_tracker.db import create_user_if_not_exists, get_user_company_info
from insight_tracker.ui.session_state import initialize_session_state
from insight_tracker.utils.cookie_manager import store_auth_cookie, load_auth_cookie, clear_auth_cookie
import logging
from insight_tracker.utils.url_manager import redirect_to_base_url, BASE_URL
from time import time
import time as time_module
from pathlib import Path
from insight_tracker.utils.logger import logger

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

def validate_token_and_get_user(token):
    logger.info("Attempting to validate token and get user info")
    try:
        # Get user info from Auth0
        response = auth0.get(
            f"https://{AUTH0_DOMAIN}/userinfo", 
            headers={"Authorization": f"Bearer {token}"}
        )
        user_info = response.json()
        
        if 'error' in user_info:
            if user_info['error'] == 'access_denied' and 'Too Many Requests' in user_info.get('error_description', ''):
                logger.warning("Auth0 rate limit hit")

                # Get reset time from headers if available
                reset_time = response.headers.get('X-RateLimit-Reset')

                if reset_time:
                    reset_seconds = int(reset_time) - int(time())
                    st.warning(f"Rate limit reached. Will reset in {reset_seconds} seconds.")
                else:
                    st.warning("Rate limit reached. Please wait a few seconds before trying again.")

                # If we have cached data, use it and redirect
                if 'user_info' in st.session_state:
                    base_url = os.getenv("BASE_URL", "/")
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={base_url}">', unsafe_allow_html=True)
                    return st.session_state.user_info

                # Otherwise, force a reauth after a short delay
                time_module.sleep(2)  # Add a small delay
                st.session_state.authentication_status = 'unauthenticated'
                return None

        # Successfully got user info, store and redirect
        st.session_state.user_info = user_info
        base_url = os.getenv("BASE_URL", "/")
        st.markdown(f'<meta http-equiv="refresh" content="0;url={base_url}">', unsafe_allow_html=True)
        return user_info

    except Exception as e:
        logger.error(f"Error validating token: {e}")
        if 'user_info' in st.session_state:
            # Use cached data if available
            base_url = os.getenv("BASE_URL", "/")
            st.markdown(f'<meta http-equiv="refresh" content="0;url={base_url}">', unsafe_allow_html=True)
            return st.session_state.user_info
        return None

def silent_sign_in():
    """Attempt to silently authenticate using stored token"""
    logger.info("Attempting silent sign-in")
    
    access_token = st.session_state.get('access_token')
    if not access_token:
        logger.debug("No access token found for silent sign-in")
        return False
        
    try:
        user_info = validate_token_and_get_user(access_token)
        if user_info:
            logger.info(f"Silent sign-in successful for user: {user_info.get('email')}")
            st.session_state.user = user_info
            st.session_state.authentication_status = 'authenticated'
            return True
        else:
            logger.warning("Silent sign-in failed - invalid token")
            st.session_state.access_token = None
            st.session_state.user = None
            return False
    except Exception as e:
        logger.error(f"Error during silent sign-in: {str(e)}")
        st.session_state.access_token = None
        st.session_state.user = None
        return False

def login():
    # First try silent sign-in
    if silent_sign_in():
        return True
        
    # If silent sign-in fails, proceed with regular login
    state = os.urandom(16).hex()
    st.session_state.oauth_state = state  # Store state in session
    
    authorization_url, _ = auth0.create_authorization_url(
        f"https://{AUTH0_DOMAIN}/authorize",
        audience=f"https://{AUTH0_DOMAIN}/userinfo",
        state=state,
        prompt='login'  # Force login prompt
    )
    
    # Store the URL for verification
    st.session_state.oauth_redirect = AUTH0_CALLBACK_URL
    st.session_state.last_auth_url = authorization_url  # Store the last auth URL
    
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
    logger.info("Starting callback handling")
    query_params = st.query_params
    logger.debug(f"Query params received: {query_params}")

    if 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        received_state = query_params['state']
        stored_state = st.session_state.get('oauth_state')
        
        try:
            # Clear state immediately to prevent reuse
            st.session_state.pop('oauth_state', None)
            
            logger.debug("Attempting to fetch token from Auth0")
            token = auth0.fetch_token(
                f"https://{AUTH0_DOMAIN}/oauth/token",
                code=code,
                redirect_uri=AUTH0_CALLBACK_URL
            )
            logger.info("Successfully fetched token from Auth0")

            access_token = token.get('access_token')
            id_token = token.get('id_token')

            user_info = auth0.get(
                f"https://{AUTH0_DOMAIN}/userinfo", 
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()
            logger.info(f"Retrieved user info for email: {user_info.get('email')}")
            
            # Store everything in session state
            st.session_state.access_token = access_token
            st.session_state.id_token = id_token
            st.session_state.user = user_info
            st.session_state.authentication_status = 'authenticated'
            
            # Store auth cookie
            store_auth_cookie(access_token)
            
            # Create user in database if needed
            success, is_new_user = create_user_if_not_exists(
                full_name=user_info.get('name', ''),
                email=user_info.get('email', ''),
                company="",
                role=""
            )
            st.session_state.is_new_user = is_new_user
            
            # Clear query parameters
            st.query_params.clear()
            
            # Log the session state after setting everything
            logger.info(f"Session state after auth setup: {dict(st.session_state)}")
            
            # Redirect to base URL
            base_url = os.getenv("BASE_URL", "/")
            st.markdown(f'<meta http-equiv="refresh" content="0;url={base_url}">', unsafe_allow_html=True)
            
            return True

        except Exception as e:
            logger.error(f"Auth callback error: {str(e)}")
            st.session_state.authentication_status = 'unauthenticated'
            return False
    else:
        logger.warning("No authorization code or state found in query params")
        return False

def logout():
    logger.info("Initiating logout")
    
    # Clear cookies and session
    clear_auth_cookie()
    st.session_state.clear()
    initialize_session_state()
    
    # Redirect using JavaScript
    redirect_to_base_url()