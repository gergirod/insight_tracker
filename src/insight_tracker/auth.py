import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import jwt
from insight_tracker.db import create_user_if_not_exists, get_user_company_info
from insight_tracker.ui.session_state import initialize_session_state
import logging

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

# Configure logging at the top of the file
logging.basicConfig(
    filename='auth.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_token_and_get_user(token):
    logging.info(f"Attempting to validate token and get user info")
    try:
        # Get user info from Auth0
        user_info = auth0.get(
            f"https://{AUTH0_DOMAIN}/userinfo", 
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        logging.info(f"Successfully retrieved user info from Auth0")
        return user_info
    except Exception as e:
        logging.error(f"Error validating token: {str(e)}")
        return None

def silent_sign_in():
    """Attempt to silently authenticate using stored token"""
    logging.info("Attempting silent sign-in")
    
    access_token = st.session_state.get('access_token')
    if not access_token:
        logging.debug("No access token found for silent sign-in")
        return False
        
    try:
        user_info = validate_token_and_get_user(access_token)
        if user_info:
            logging.info(f"Silent sign-in successful for user: {user_info.get('email')}")
            st.session_state.user = user_info
            st.session_state.authentication_status = 'authenticated'
            return True
        else:
            logging.warning("Silent sign-in failed - invalid token")
            st.session_state.access_token = None
            st.session_state.user = None
            return False
    except Exception as e:
        logging.error(f"Error during silent sign-in: {str(e)}")
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
    logging.info("Starting callback handling")
    query_params = st.query_params
    logging.debug(f"Query params received: {query_params}")

    if 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        received_state = query_params['state']
        stored_state = st.session_state.get('oauth_state')
        
        logging.debug(f"Received state: {received_state}")
        logging.debug(f"Stored state: {stored_state}")
        
        # Clear query params immediately to prevent reuse
        st.query_params.clear()
        
        # Skip state verification if we don't have a stored state
        if stored_state and received_state != stored_state:
            logging.error("State parameter mismatch")
            logging.debug(f"Stored state: {stored_state}")
            logging.debug(f"Received state: {received_state}")
            return False

        try:
            # Clear state immediately to prevent reuse
            st.session_state.pop('oauth_state', None)
            
            logging.debug("Attempting to fetch token from Auth0")
            token = auth0.fetch_token(
                f"https://{AUTH0_DOMAIN}/oauth/token",
                code=code,
                redirect_uri=AUTH0_CALLBACK_URL
            )
            logging.info("Successfully fetched token from Auth0")

            access_token = token.get('access_token')
            id_token = token.get('id_token')  # Also store the ID token if available
            logging.debug(f"Access token obtained: {access_token[:10]}...")

            user_info = auth0.get(
                f"https://{AUTH0_DOMAIN}/userinfo", 
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()
            logging.info(f"Retrieved user info for email: {user_info.get('email')}")
            
            # Store everything in session state
            st.session_state.access_token = access_token
            st.session_state.id_token = id_token  # Store ID token
            st.session_state.user = user_info
            st.session_state.authentication_status = 'authenticated'
            
            success, is_new_user = create_user_if_not_exists(
                full_name=user_info.get('name', ''),
                email=user_info.get('email', ''),
                company="",
                role=""
            )
            
            logging.info(f"User creation/update status - Success: {success}, New user: {is_new_user}")
            st.session_state.is_new_user = is_new_user
            
            return True

        except Exception as e:
            logging.error(f"Error during callback handling: {str(e)}", exc_info=True)
            # Don't clear session state on error, just return False
            return False
    else:
        logging.warning("No authorization code or state found in query params")
        return False

def logout():
    logging.info("Initiating logout")
    logging.debug(f"Session state before logout: {dict(st.session_state)}")
    
    st.session_state.user = None
    st.session_state.authentication_status = 'unauthenticated'
    
    logging.info("User logged out successfully")
    logging.debug(f"Session state after logout: {dict(st.session_state)}")
    
    st.success("You have been logged out successfully.")
    st.rerun()