import sqlite3
import streamlit as st
from insight_tracker.auth import handle_callback, logout, try_silent_login
from insight_tracker.db import getUserByEmail, init_db, init_recent_searches_db, alter_profile_searches_table, init_user_company_db, get_user_company_info
from insight_tracker.ui.profile_insight_section import profile_insight_section
from insight_tracker.ui.company_insight_section import company_insight_section
from insight_tracker.ui.recent_searches_section import recent_searches_section
from insight_tracker.ui.login_section import auth_section
from insight_tracker.ui.settings_section import settings_section
from insight_tracker.ui.side_bar import display_side_bar
from insight_tracker.ui.session_state import initialize_session_state
from insight_tracker.ui.onboarding_section import onboarding_section
from insight_tracker.ui.components.loading_dialog import show_loading_dialog
from insight_tracker.auth import get_auth_cookie
import logging

# Configure logging
logging.basicConfig(filename='authentication.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def check_and_alter_table():
    """Check if the table needs alteration and perform it if necessary."""
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    try:
        # Check if the column exists
        c.execute("PRAGMA table_info(profile_searches)")
        columns = [column[1] for column in c.fetchall()]
        if 'current_company' not in columns or 'current_company_url' not in columns:
            alter_profile_searches_table()
    finally:
        conn.close()

st.set_page_config(
    page_title="Insight Tracker",
    page_icon="🎯",
    initial_sidebar_state="expanded",
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state and database
initialize_session_state()
init_db()
init_recent_searches_db()
check_and_alter_table()  # Check and alter the table if necessary
init_user_company_db()

def show_loading_screen():
    loading_container = show_loading_dialog(
        title="Preparing Your Insights",
        description="Please wait while we set up your personalized dashboard with AI-powered recommendations and insights.",
        loading_message="Loading your workspace..."
    )
    return loading_container

def handle_auth():
    """Handle authentication process"""
    print("Handling authentication")
    
    # First try silent login with stored token
    user_info = try_silent_login()
    if user_info:
        return True
    
    # If silent login failed, check for auth callback
    if 'code' in st.query_params and st.session_state.user is None:
        print("Handling callback")
        if handle_callback():
            return True
    
    return st.session_state.user is not None

def check_user_setup_complete(user, user_company) -> bool:
    """
    Check if user has completed their setup
    Returns False if any required data is missing
    """
    if not user:
        return False
    
    # Check if user has basic data
    if not user[1] or not user[3] or not user[4]:  # name, role, company
        return False
    
    # Check if user has company data saved
    if not user_company:
        return False
        
    return True

def display_main_content(user):
    """Display main content based on selected navigation option"""
    logging.info("User final : " + user)
    user_company = get_user_company_info(user[2])
    
    # Show onboarding only for new users who haven't completed setup
    if st.session_state.get('is_new_user', False) and not user_company:
        onboarding_section(user[2])
        return
    
    # For existing users or after onboarding completion, show main content
    display_side_bar()
    
    # Handle navigation
    if st.session_state.nav_bar_option_selected == "Recent Searches":
        recent_searches_section()
    elif st.session_state.nav_bar_option_selected == "Profile Insight":
        profile_insight_section()
    elif st.session_state.nav_bar_option_selected == "Company Insight":
        company_insight_section()
    elif st.session_state.nav_bar_option_selected == "Settings":
        settings_section(user, user_company, setup_complete=True)
    elif st.session_state.nav_bar_option_selected == "Logout":
        logout()
    else:
        profile_insight_section()  # Default to Profile Insight if no selection

def main():
    # Try silent login first if user is not authenticated
    logging.info("Authentication status: 1 " + st.session_state.authentication_status)
    if st.session_state.authentication_status != 'authenticated':
        logging.info("Authentication status: 2 " + st.session_state.authentication_status)
        user_info = try_silent_login()
        if user_info:
            logging.info("Authentication status: 3 " + st.session_state.authentication_status)
            display_main_content(user_info)

    
    if st.session_state.authentication_status == 'checking':
        logging.info("Authentication status: 4 " + st.session_state.authentication_status)
        loading_container = show_loading_screen()
        if handle_auth():
            logging.info("Authentication status: 5 " + st.session_state.authentication_status)
            st.session_state.authentication_status = 'authenticated'
            user_email = st.session_state.user.get('email')
            user = getUserByEmail(user_email)
            display_main_content(user)
        else:
            logging.info("Authentication status: 6 " + st.session_state.authentication_status)
            st.session_state.authentication_status = 'unauthenticated'
            st.rerun()
    elif st.session_state.authentication_status == 'authenticated':
        if st.session_state.user is None:
            logging.info("Authentication status: 7 " + st.session_state.authentication_status)
            # If user is None but status is authenticated, try silent login
            user_info = try_silent_login()
            if not user_info:
                logging.info("Authentication status: 8 " + st.session_state.authentication_status)
                st.session_state.authentication_status = 'unauthenticated'
            st.rerun()
        else:
            logging.info("Authentication status: 9 " + st.session_state.authentication_status)
            user_email = st.session_state.user.get('email')
            user = getUserByEmail(user_email)
            logging.info("Authentication status: 10 " + user_email)
            logging.info("User final 1 : " + str(user))
            if user is None:
                logging.info("Authentication status: 12.1 " + st.session_state.authentication_status)
                auth_section()
            else:
                logging.info("Authentication status: 12.2 " + st.session_state.authentication_status)
                display_main_content(user)
    else:  # unauthenticated
        logging.info("Authentication status: 13 " + st.session_state.authentication_status)
        auth_section()

if __name__ == "__main__":
    main()