import streamlit as st
from insight_tracker.auth import login

def auth_section():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size:20px !important;
    }
    .feature-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .cta-button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<p class="big-font">Welcome to Insight Tracker</p>', unsafe_allow_html=True)
    st.markdown('<p class="medium-font">Unlock powerful insights and supercharge your outreach</p>', unsafe_allow_html=True)

    # Main features section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-box">
        <h3>🔍 Profile Insights</h3>
        <p>Gain deep understanding of individual profiles. Uncover key information, interests, and potential connection points to make your outreach more personal and effective.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-box">
        <h3>🏢 Company Analysis</h3>
        <p>Dive into comprehensive company data. Understand industry trends, key players, and company culture to tailor your approach for maximum impact.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-box">
    <h3>✉️ Smart Outreach Generator</h3>
    <p>Leverage our AI-powered email generator to create personalized, compelling outreach messages. Use the insights gathered to craft emails that resonate with your recipients and increase your response rates.</p>
    </div>
    """, unsafe_allow_html=True)

    # Call to Action
    st.markdown("### Ready to elevate your outreach game?")
    
    col3, col4, col5 = st.columns([1,1,1])
    
    with col4:
        login()

    # Testimonial or extra info
    st.markdown("""
    <div style="margin-top: 50px; text-align: center; font-style: italic;">
    "Insight Tracker has revolutionized our outreach strategy. We've seen a 40% increase in response rates!" - Jane Doe, Marketing Director
    </div>
    """, unsafe_allow_html=True)