import streamlit as st

def store_auth_cookie(access_token):
    """Store authentication data in cookies"""
    if access_token:
        st.cookies.set('access_token', access_token, 
                      expires_at=3600,  # 1 hour expiry
                      key='auth_cookie',
                      secure=True,
                      httponly=True)

def load_auth_cookie():
    """Load authentication data from cookies"""
    access_token = st.cookies.get('access_token')
    if access_token:
        st.session_state.access_token = access_token
        return True
    return False

def clear_auth_cookie():
    """Clear authentication cookies"""
    st.cookies.delete('access_token') 