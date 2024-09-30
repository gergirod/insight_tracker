import streamlit as st
from insight_tracker.auth import login

def auth_section():
    # Minimal CSS for clean and centered layout without scroll issues
    st.markdown("""
        <style>
        /* Center content vertically and horizontally */
        .full-height-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 0;
        }

        /* Title Styling */
        .main-title {
            font-size: 2.5rem;
            color: #333;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* Description Styling */
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 30px;
        }

        </style>
    """, unsafe_allow_html=True)

    # Full height container to ensure proper centering
    st.markdown('<div class="full-height-container">', unsafe_allow_html=True)
    
    # Start content structure inside the centered container
    st.markdown('<div>', unsafe_allow_html=True)
    
    # Display title and subtitle
    st.markdown('<h1 class="main-title">Welcome to Insight Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Please log in or sign up to continue</p>', unsafe_allow_html=True)
    
    # Display the login button
    login()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close the inner div
    
    st.markdown('</div>', unsafe_allow_html=True)  # Clo