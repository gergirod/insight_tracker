import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv

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
    """
    Initiates the Auth0 login process.

    """
    print('user' not in st.session_state)
    print(st.session_state)
    if st.session_state.user is None:
        # Create the authorization URL for login
        authorization_url, _ = auth0.create_authorization_url(
            f"https://{AUTH0_DOMAIN}/authorize",
            audience=f"https://{AUTH0_DOMAIN}/userinfo",
        )
        # Display the login link
        st.markdown(f'<a href="{authorization_url}" target="_self">Login with Auth0</a>', unsafe_allow_html=True)
    else:
        # If the user is logged in, greet them and show the logout option
        # st.write(f"Welcome, {st.session_state.user['name']}!")
        if st.button("Logout"):
            del st.session_state['user']
            st.experimental_rerun()

def signup():
    """
    Initiates the Auth0 signup process.
    """
    # Create the signup URL
    signup_url = f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid%20profile%20email&screen_hint=signup"
    
    # Display the signup button
    if st.button("Sign Up with Auth0"):
        st.markdown(f'<meta http-equiv="refresh" content="0;url={signup_url}">', unsafe_allow_html=True)

def handle_callback():
    """
    Handle the Auth0 callback, exchange authorization code for tokens, and retrieve user info.
    """
    # Use Streamlit's built-in function to get the query parameters
    query_params = st.query_params

    print(query_params)

    # Check if the authorization code exists in the query parameters
    if 'code' in query_params:
        code = query_params['code']  # The code is returned as a list, so we take the first element

        print(code)

        try:
            # Exchange the authorization code for access and ID tokens
            token = auth0.fetch_token(
                f"https://{AUTH0_DOMAIN}/oauth/token",
                code=code,
                redirect_uri=AUTH0_CALLBACK_URL
            )

            print(token)

            # Fetch the user's profile info from Auth0
            access_token = token.get('access_token')

            print(access_token)

            # Fetch the user's profile info from Auth0 using the access token in the Authorization header
            user_info = auth0.get(
                f"https://{AUTH0_DOMAIN}/userinfo", 
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            # Store user information in the session state
            st.session_state.user = user_info

            # Refresh the app to reflect the login state
            st.rerun()

        except Exception as e:
            st.error(f"Error during callback handling: {e}")
    else:
        st.error("Authorization code not found.")
