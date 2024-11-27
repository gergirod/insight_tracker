import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import jwt
from insight_tracker.db import create_user_if_not_exists, get_user_company_info

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
            
            # Store whether user is new in session state
            st.session_state.is_new_user = is_new_user
            
            if success:
                print(f"Created new user: {user_info.get('email')}")
            else:
                print(f"User already exists: {user_info.get('email')}")

            print(f"User info company check: {user_info}")
            # Retrieve and set user company info
            user_company = get_user_company_info(user_info.get('email'))
            print(f"Retrieved user company: {user_company}")
            st.session_state.user_company = user_company

            print(f"User info: {user_info}")
            st.session_state.user = user_info
            st.session_state.authentication_status = 'authenticated'
            st.query_params.clear()
            return True

        except Exception as e:
            print(f"Error during callback handling: {e}")
    else:
        print("Authorization code not found.")
    return False

def logout():
    st.session_state.user = None
    st.session_state.authentication_status = 'unauthenticated'
    st.success("You have been logged out successfully.")
    st.rerun()