import streamlit as st
from streamlit_option_menu import option_menu
from insight_tracker.utils.logger import logger

def display_side_bar():
    """Display the sidebar navigation"""
    # First, let's try a basic sidebar to verify it works
    with st.sidebar:
        st.write("### Navigation")
        
        # Debug info
        st.write("Debug info:")
        st.write(f"User: {st.session_state.get('user')}")
        st.write(f"Auth status: {st.session_state.get('authentication_status')}")
        
        # Basic navigation buttons
        if st.session_state.get('user') is not None:
            if st.button("Profile Insight"):
                st.session_state.nav_bar_option_selected = "Profile Insight"
                st.rerun()
            if st.button("Company Insight"):
                st.session_state.nav_bar_option_selected = "Company Insight"
                st.rerun()
            if st.button("Recent Searches"):
                st.session_state.nav_bar_option_selected = "Recent Searches"
                st.rerun()
            if st.button("Settings"):
                st.session_state.nav_bar_option_selected = "Settings"
                st.rerun()
            if st.button("Logout"):
                st.session_state.nav_bar_option_selected = "Logout"
                st.rerun()

    return st.session_state.nav_bar_option_selected