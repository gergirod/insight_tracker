import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Auth0 configuration
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

# Initialize Auth0 client
auth0 = OAuth2Session(
    AUTH0_CLIENT_ID,
    AUTH0_CLIENT_SECRET,
    scope='openid profile email'
)

def login():
    if st.session_state.user not in st.session_state:
        authorization_url, _ = auth0.create_authorization_url(
            f"https://{AUTH0_DOMAIN}/authorize"
        )
        st.markdown(f'<a href="{authorization_url}" target="_self">Login with Auth0</a>', unsafe_allow_html=True)
    else:
        st.write(f"Welcome {st.session_state.user['name']}!")
        if st.button("Logout"):
            del st.session_state['user']
            st.experimental_rerun()

def signup():
    signup_url = f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid%20profile%20email&screen_hint=signup"
    
    if st.button("Sign Up with Auth0"):
        st.markdown(f'<meta http-equiv="refresh" content="0;url={signup_url}">', unsafe_allow_html=True)

def handle_callback():
    code = st.query_params()['code'][0]
    token = auth0.fetch_token(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        code=code,
        redirect_uri=AUTH0_CALLBACK_URL
    )
    user_info = auth0.get(f"https://{AUTH0_DOMAIN}/userinfo").json()
    st.session_state.user = user_info