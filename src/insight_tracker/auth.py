import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import json
import streamlit.components.v1 as components
import jwt
import time
from streamlit_cookies_controller import CookieController

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

def get_cookie():
    try:
        return CookieController().get("id_token")
    except Exception as e:
        print(f"Error getting cookie: {e}")
        return None

def set_cookie(token):
    CookieController().set("id_token", token)

def remove_cookie():
    try:
        CookieController().remove("id_token")
    except Exception as e:
        print(f"Error removing cookie: {e}")

def validate_token_and_get_user(token):
    try:
        # Decode the token
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Get user info from Auth0
        user_info = auth0.get(
            f"https://{AUTH0_DOMAIN}/userinfo", 
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        
        return user_info
    except Exception as e:
        print(f"Error validating token: {e}")
        return None

def login():
    if st.session_state.user is None:
        authorization_url, _ = auth0.create_authorization_url(
            f"https://{AUTH0_DOMAIN}/authorize",
            audience=f"https://{AUTH0_DOMAIN}/userinfo",
        )
        st.markdown(f'''
        <a href="{authorization_url}" target="_self" style="
            display: inline-block;
            background-color: transparent;
            color: #007bff;
            padding: 10px 30px;
            font-size: 1rem;
            font-weight: 600;
            border: 2px solid #007bff;
            border-radius: 50px;
            text-decoration: none;
            transition: all 0.3s ease;
            " onmouseover="this.style.backgroundColor='#007bff'; this.style.color='white';" 
            onmouseout="this.style.backgroundColor='transparent'; this.style.color='#007bff';">
            Login with Auth0
        </a>
    ''', unsafe_allow_html=True)

def signup():
    signup_url = f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid%20profile%20email&screen_hint=signup"
    
    if st.button("Sign Up with Auth0"):
        st.markdown(f'<meta http-equiv="refresh" content="0;url={signup_url}">', unsafe_allow_html=True)

def handle_callback():
    query_params = st.query_params

    if 'code' in query_params:
        code = query_params['code']

        try:
            token = auth0.fetch_token(
                f"https://{AUTH0_DOMAIN}/oauth/token",
                code=code,
                redirect_uri=AUTH0_CALLBACK_URL
            )

            access_token = token.get('access_token')
            id_token = token.get('id_token')

            print(f"Received id_token: {id_token[:10]}...")

            user_info = auth0.get(
                f"https://{AUTH0_DOMAIN}/userinfo", 
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            st.session_state.user = user_info
            set_cookie(id_token)
            st.rerun()

        except Exception as e:
            print(f"Error during callback handling: {e}")
    else:
        print("Authorization code not found.")

def logout():
    st.session_state.user = None
    remove_cookie()
    st.success("You have been logged out successfully.")
    st.rerun()