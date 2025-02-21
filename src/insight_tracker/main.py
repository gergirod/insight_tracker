import sqlite3
import streamlit as st
# First Streamlit command must be set_page_config
st.set_page_config(
    page_title="Insight Tracker",
    page_icon="🎯",
    initial_sidebar_state="expanded",
)

# Initialize cookie manager early
from insight_tracker.utils.cookie_manager import get_cookie_manager
_ = get_cookie_manager()  # Initialize the global instance

# Rest of the imports
from insight_tracker.auth import handle_callback, logout, validate_token_and_get_user, silent_sign_in
from insight_tracker.utils.cookie_manager import load_auth_cookie, clear_auth_cookie, get_cookie_manager
from insight_tracker.db import getUserByEmail, init_db, init_recent_searches_db, check_and_alter_table, init_user_company_db, get_user_company_info
from insight_tracker.ui.profile_insight_section import profile_insight_section
from insight_tracker.ui.company_insight_section import company_insight_section
from insight_tracker.ui.recent_searches_section import recent_searches_section
from insight_tracker.ui.login_section import auth_section
from insight_tracker.ui.settings_section import settings_section
from insight_tracker.ui.side_bar import display_side_bar
from insight_tracker.ui.session_state import initialize_session_state
from insight_tracker.ui.onboarding_section import onboarding_section
from insight_tracker.ui.components.loading_dialog import show_loading_dialog
from insight_tracker.utils.url_manager import redirect_to_base_url, BASE_URL
from insight_tracker.utils.logger import logger

# Initialize cookie manager
cookie_manager = get_cookie_manager()

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
    logger.info("Starting authentication handling")
    logger.debug(f"Current session state: {dict(st.session_state)}")
    
    # Check if we already have a valid session
    if st.session_state.get('access_token') and st.session_state.user:
        try:
            # Validate the existing token
            user_info = validate_token_and_get_user(st.session_state.access_token)
            if user_info:
                logger.info("Existing session validated successfully")
                st.session_state.user = user_info
                st.session_state.authentication_status = 'authenticated'
                return True
            else:
                logger.warning("Existing token validation failed")
                st.session_state.authentication_status = 'unauthenticated'
                st.session_state.user = None
                st.session_state.access_token = None
        except Exception as e:
            logger.error(f"Error validating existing token: {str(e)}")
            st.session_state.authentication_status = 'unauthenticated'
            st.session_state.user = None
            st.session_state.access_token = None
    
    # Handle new authentication
    if 'code' in st.query_params:
        logger.info("Auth code found in query params")
        if handle_callback():
            logger.info("Callback handled successfully")
            return True
        logger.warning("Callback handling failed")
    
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
    logger.debug(f"Displaying main content for user: {user}")
    
    # Get user email from the dictionary
    user_email = user.get('email')
    saved_user = getUserByEmail(user_email)
    user_company = get_user_company_info(user_email)
    
    # Show onboarding only for new users who haven't completed setup
    if st.session_state.get('is_new_user', False) and not user_company:
        onboarding_section(user_email)
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
        settings_section(saved_user, user_company, setup_complete=True)
    elif st.session_state.nav_bar_option_selected == "Logout":
        logout()
    else:
        profile_insight_section()  # Default to Profile Insight if no selection

def main():
    logger.info("Starting application")
    
    # Debug current state
    logger.info(f"Session state at start: {dict(st.session_state)}")
    logger.info(f"Query params at start: {dict(st.query_params)}")
    
    # First check for valid cookies and try silent sign-in
    if not st.session_state.get('authentication_status'):
        logger.info("No authentication status found")
        if load_auth_cookie():
            logger.info("Found valid auth cookie, attempting silent sign-in")
            if silent_sign_in():
                logger.info("Silent sign-in successful")
                logger.info(f"User after silent sign-in: {st.session_state.get('user')}")
                display_main_content(st.session_state.user)
                return
            else:
                logger.info("Silent sign-in failed (expired/invalid token)")
                clear_auth_cookie()
                st.session_state.access_token = None
                st.session_state.user = None
                st.session_state.authentication_status = 'unauthenticated'
    else:
        logger.info(f"Existing auth status: {st.session_state.get('authentication_status')}")
        # If authenticated, verify cookie still exists
        if st.session_state.authentication_status == 'authenticated':
            if load_auth_cookie():
                logger.info("Authentication verified with cookie")
                display_main_content(st.session_state.user)
                return
            else:
                logger.info("Cookie missing for authenticated session, clearing state")
                clear_auth_cookie()
                st.session_state.authentication_status = 'unauthenticated'
    
    # Handle new authentication callback if present
    if 'code' in st.query_params:
        logger.info("Processing auth callback")
        if handle_auth():
            logger.info("Auth successful, displaying main content")
            logger.info(f"Session state after auth: {dict(st.session_state)}")
            display_main_content(st.session_state.user)
            return
        else:
            logger.warning("Auth failed")
            st.session_state.authentication_status = 'unauthenticated'
    
    # If we get here, show the initial screen
    logger.info("Showing initial login screen")
    logger.info("No valid authentication found, showing login")
    auth_section()

if __name__ == "__main__":
    main()