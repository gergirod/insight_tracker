import streamlit as st
from insight_tracker.auth import login, auth0, AUTH0_DOMAIN, AUTH0_CALLBACK_URL

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
    
    # Enhanced features highlight before login
    st.markdown("""
    <div style="
        text-align: center;
        margin-top: 0.5rem;    
        margin-left: auto;      
        margin-right: auto; 
        max-width: 800px;
        padding: 0.5rem;">
        <h2 style="
            color: #1E88E5;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;">
            Ready to unlock meaningful connections?
        </h2>
        <div style="
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;">
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                color: #666;">
                <span style="color: #1E88E5;">✓</span> AI-Powered Insights
            </div>
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                color: #666;">
                <span style="color: #1E88E5;">✓</span> Smart Outreach
            </div>
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                color: #666;">
                <span style="color: #1E88E5;">✓</span> Meeting Preparation
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Update login button to use base URL
    login_url = auth0.create_authorization_url(
        f"https://{AUTH0_DOMAIN}/authorize",
        redirect_uri=AUTH0_CALLBACK_URL,
        audience=f"https://{AUTH0_DOMAIN}/userinfo",
    )[0]
    
    st.markdown(f'''
    <div style="text-align: center;">
        <a href="{login_url}" target="_self" style="
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
    </div>
    ''', unsafe_allow_html=True)

    # Enhanced testimonial
    st.markdown("""
    <div style="
        text-align: center;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        padding: 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <div style="
            font-style: italic;
            color: #555;
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 1rem;">
            "Insight Tracker transformed how we connect with people. The AI-powered analysis helps us understand our contacts better, evaluate opportunities more effectively, and prepare for meaningful interactions."
        </div>
        <div style="
            color: #1E88E5;
            font-weight: 500;">
            Sarah Chen, Innovation Lead
        </div>
    </div>
    """, unsafe_allow_html=True)