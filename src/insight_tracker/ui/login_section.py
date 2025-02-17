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
        .auth-features {
            margin-top: 2rem;
            text-align: center;
            color: #666;
            width: 100%;
            max-width: 500px;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .feature-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: left;
        }
        .feature-icon {
            font-size: 1.5rem;
            color: #1E88E5;
            min-width: 24px;
        }
        .feature-text {
            font-size: 0.95rem;
            color: #444;
            line-height: 1.3;
        }
        .auth-info {
            margin-top: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #666;
            font-size: 0.9rem;
            padding: 8px 16px;
            background: #f8f9fa;
            border-radius: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-container">
            <h1 class="auth-title">Welcome to Insight Tracker</h1>
            <p class="auth-subtitle">Your all-in-one solution for tracking business insights and managing professional relationships</p>
            
            <div class="auth-features">
                <div class="feature-grid">
                    <div class="feature-item">
                        <div class="feature-icon">🎯</div>
                        <div class="feature-text">Track and analyze business insights efficiently</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🤝</div>
                        <div class="feature-text">Manage professional relationships effectively</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📊</div>
                        <div class="feature-text">Comprehensive analytics and reporting</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🔒</div>
                        <div class="feature-text">Secure and private data management</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🔍</div>
                        <div class="feature-text">Advanced search and filtering capabilities</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📱</div>
                        <div class="feature-text">Access your data from anywhere, anytime</div>
                    </div>
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