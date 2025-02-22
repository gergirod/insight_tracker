import streamlit as st
from insight_tracker.utils.logger import logger

def display_side_bar():
    """Display the sidebar navigation"""
    inject_css()

    with st.sidebar:
        if st.session_state.get('user') is not None:
            # App name first
            st.markdown("### Insight Tracker")
            # Divider
            st.markdown("---")
            
            # Get user's name from session state
            user_name = st.session_state.user.get('name', 'there')  # 'there' as fallback
            
            # Welcome message below app name
            st.markdown(f'<p class="welcome">👋 Hello, {user_name}!</p>', unsafe_allow_html=True)
            
            # Navigation options with icons
            options = {
                "Profile Insight": "👤",
                "Company Insight": "🏢",
                "Recent Searches": "🕒",
                "Settings": "⚙️",
                "Logout": "🚪"
            }
            
            current_option = st.session_state.get('nav_bar_option_selected', 'Profile Insight')
            
            for option, icon in options.items():
                is_selected = current_option == option
                style = "font-weight: 600;" if is_selected else "font-weight: 400;"
                if st.button(f"{icon} {option}", key=f"nav_{option}", use_container_width=True):
                    st.session_state.nav_bar_option_selected = option

    return st.session_state.nav_bar_option_selected

def inject_css():
    st.markdown("""
        <style>
        /* Style for the navigation buttons - made more specific */
        section[data-testid="stSidebar"] .stButton > button,
        .stButton > button[kind="secondary"],
        .stButton > button {
            width: 100% !important;
            background-color: #1E88E5 !important;
            color: white !important;
            padding: 14px 48px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            border-radius: 50px !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease !important;
            margin: 10px 0 !important;
            letter-spacing: 0.3px !important;
            text-align: center !important;
        }

        /* Hover state - made more specific */
        section[data-testid="stSidebar"] .stButton > button:hover,
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:hover {
            background-color: #1976D2 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            transform: translateY(-1px) !important;
        }

        /* Active state - made more specific */
        section[data-testid="stSidebar"] .stButton > button:active,
        .stButton > button[kind="secondary"]:active,
        .stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* Focus state - made more specific */
        section[data-testid="stSidebar"] .stButton > button:focus,
        .stButton > button[kind="secondary"]:focus,
        .stButton > button:focus {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }
        
        .welcome {
            color: #495057;
            font-size: 1rem;
            margin: 0.5rem 0 1rem 1rem;
        }
        </style>
    """, unsafe_allow_html=True)