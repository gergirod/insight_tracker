import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
from insight_tracker.db import create_user_if_not_exists
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

def login():
    """Create login URL and display button"""
    authorization_url, _ = auth0.create_authorization_url(
        f"https://{AUTH0_DOMAIN}/authorize",
        audience=f"https://{AUTH0_DOMAIN}/userinfo"
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
            margin: 10px 0;">
            Continue with Auth0
        </a>
    </div>
    ''', unsafe_allow_html=True)

def handle_callback():
    """Handle the Auth0 callback after login"""
    try:
        code = st.query_params['code']
        token = auth0.fetch_token(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            code=code,
            redirect_uri=AUTH0_CALLBACK_URL
        )

        access_token = token.get('access_token')
        
        # Get user info from Auth0
        user_info = auth0.get(
            f"https://{AUTH0_DOMAIN}/userinfo", 
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        
        # Store user info in session state
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
        
        # Clear query parameters
        st.query_params.clear()
        
        # Rerun the app to show authenticated content
        st.rerun()

    except Exception as e:
        logging.error(f"Auth callback error: {str(e)}")
        return False

def logout():
    """Clear session state and log out user"""
    st.session_state.user = None
    st.session_state.authentication_status = 'unauthenticated'
    st.rerun()