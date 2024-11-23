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
    st.markdown('<p class="medium-font">Unlock powerful insights and build meaningful connections</p>', unsafe_allow_html=True)

    # Main features section in 2 rows
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

    # New row with 3 columns for action features
    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown("""
        <div class="feature-box">
        <h3>✉️ Smart Outreach</h3>
        <p>Generate personalized, compelling outreach messages using AI. Create emails that resonate with your recipients and boost response rates through data-driven insights.</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-box">
        <h3>🎯 Fit Evaluator</h3>
        <p>Assess profile-company compatibility with precision. Get detailed analysis of alignment, potential challenges, and strategic recommendations for successful engagement.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature-box">
        <h3>📅 Meeting Preparation</h3>
        <p>Get AI-powered meeting strategies tailored to your context. Includes agenda planning, key talking points, and strategic recommendations for successful interactions.</p>
        </div>
        """, unsafe_allow_html=True)

    # Call to Action
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    st.markdown("""
    <h3 style="text-align: center;">Ready to unlock meaningful connections?</h3>
    """, unsafe_allow_html=True)
    
    login_col1, login_col2, login_col3 = st.columns([1,1,1])
    
    with login_col2:
        login()

    # Testimonial or extra info
    st.markdown("""
    <div style="margin-top: 50px; text-align: center; font-style: italic;">
    "Insight Tracker transformed how we connect with people. The AI-powered analysis helps us understand our contacts better, evaluate opportunities more effectively, and prepare for meaningful interactions." - Sarah Chen, Innovation Lead
    </div>
    """, unsafe_allow_html=True)