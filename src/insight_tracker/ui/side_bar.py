import streamlit as st
from streamlit_option_menu import option_menu
from insight_tracker.utils.logger import logger

def display_side_bar():
    """Display the sidebar navigation"""
    # Custom CSS for better button styling
    st.markdown("""
        <style>
        .stButton button {
            width: 100%;
            text-align: left;
            padding: 15px;
            margin: 5px 0;
            border: none;
            background-color: transparent;
            color: #495057;
            font-size: 16px;
        }
        
        .stButton button:hover {
            background-color: #f8f9fa;
            color: #0d6efd;
        }
        
        /* Style for active button */
        .stButton button[data-active="true"] {
            background-color: #e7f1ff;
            color: #0d6efd;
            font-weight: 500;
        }
        
        /* Hide debug info in production */
        .debug-info {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## Insight Tracker", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.session_state.get('user') is not None:
            # Create a container for buttons
            nav_container = st.container()
            
            with nav_container:
                current_page = st.session_state.get('nav_bar_option_selected', 'Profile Insight')
                
                # Navigation buttons with icons
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.markdown("👤")
                with col2:
                    if st.button("Profile Insight", key="profile",
                               help="View and analyze profile insights"):
                        st.session_state.nav_bar_option_selected = "Profile Insight"
                        st.rerun()
                
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.markdown("🏢")
                with col2:
                    if st.button("Company Insight", key="company",
                               help="Explore company insights"):
                        st.session_state.nav_bar_option_selected = "Company Insight"
                        st.rerun()
                
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.markdown("🕒")
                with col2:
                    if st.button("Recent Searches", key="recent",
                               help="View your recent searches"):
                        st.session_state.nav_bar_option_selected = "Recent Searches"
                        st.rerun()
                
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.markdown("⚙️")
                with col2:
                    if st.button("Settings", key="settings",
                               help="Manage your preferences"):
                        st.session_state.nav_bar_option_selected = "Settings"
                        st.rerun()
                
                st.markdown("---")
                
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.markdown("🚪")
                with col2:
                    if st.button("Logout", key="logout",
                               help="Sign out of your account"):
                        st.session_state.nav_bar_option_selected = "Logout"
                        st.rerun()

    return st.session_state.nav_bar_option_selected