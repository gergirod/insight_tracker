import streamlit as st
from insight_tracker.auth import login

def auth_section():
    """Display the authentication section with login button"""
    st.markdown("""
        <style>
        .auth-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            margin-top: 2rem;
        }
        .auth-title {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: #1E88E5;
        }
        .auth-subtitle {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 2rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-container">
            <h1 class="auth-title">Welcome to Insight Tracker</h1>
            <p class="auth-subtitle">Please log in to continue</p>
        </div>
    """, unsafe_allow_html=True)

    # Display the login button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        login()