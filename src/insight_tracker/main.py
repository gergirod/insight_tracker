import streamlit as st
from insight_tracker.auth import handle_callback, get_cookie, logout, validate_token_and_get_user, set_cookie
from insight_tracker.db import getUserByEmail, init_db
from insight_tracker.ui.profile_insight_section import profile_insight_section
from insight_tracker.ui.company_insight_section import company_insight_section
from insight_tracker.ui.login_section import auth_section
from insight_tracker.ui.settings_section import settings_section
from insight_tracker.ui.side_bar import display_side_bar
from insight_tracker.ui.session_state import initialize_session_state

# Initialize session state and database
initialize_session_state()
init_db()

def handle_auth():
    """Handle authentication process"""
    print("Handling authentication")
    if 'code' in st.query_params and st.session_state.user is None:
        print("Handling callback")
        handle_callback()
    
    if st.session_state.user is None:
        token = get_cookie()
        if token:
            user_info = validate_token_and_get_user(token)
            if user_info:
                st.session_state.user = user_info
                st.rerun()
    
    if st.session_state.user is None:
        auth_section()
        return False
    
    return True

def display_main_content(user):
    """Display main content based on selected navigation option"""
    display_side_bar()
    
    if st.session_state.nav_bar_option_selected == "Profile Insight":
        profile_insight_section()
    elif st.session_state.nav_bar_option_selected == "Company Insight":
        company_insight_section()
    elif st.session_state.nav_bar_option_selected == "Settings":
        settings_section(user)
    elif st.session_state.nav_bar_option_selected == "Logout":
        logout()
    else:
        st.write("Please select an option from the sidebar.")

def main():    
    if not handle_auth():
        return
    
    user_email = st.session_state.user.get('email')
    user = getUserByEmail(user_email)
    
    display_main_content(user)

if __name__ == "__main__":
    main()