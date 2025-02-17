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
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        .auth-title {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #1E88E5;
            font-weight: 600;
        }
        .auth-subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
            text-align: center;
            line-height: 1.5;
        }
        .auth-info {
            margin-top: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #666;
            font-size: 0.9rem;
        }
        .auth-features {
            margin-top: 2rem;
            text-align: center;
            color: #666;
        }
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 1rem 0;
        }
        .feature-item {
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-container">
            <h1 class="auth-title">Welcome to Insight Tracker</h1>
            <p class="auth-subtitle">Your all-in-one solution for tracking business insights and managing professional relationships</p>
            
            <div class="auth-features">
                <div class="feature-list">
                    <div class="feature-item">✨ Track business insights efficiently</div>
                    <div class="feature-item">🔒 Secure and private</div>
                    <div class="feature-item">📊 Comprehensive analytics</div>
                    <div class="feature-item">🤝 Better relationship management</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Center the login button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        login()
        
    # Add secure authentication info
    st.markdown("""
        <div class="auth-info">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#666">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
            </svg>
            Secure authentication powered by Auth0
        </div>
    """, unsafe_allow_html=True)