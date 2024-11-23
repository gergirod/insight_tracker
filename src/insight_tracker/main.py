import sqlite3
import streamlit as st
from insight_tracker.auth import handle_callback, get_cookie, logout, validate_token_and_get_user
from insight_tracker.db import getUserByEmail, init_db, init_recent_searches_db, alter_profile_searches_table, init_user_company_db, get_user_company_info
from insight_tracker.ui.profile_insight_section import profile_insight_section
from insight_tracker.ui.company_insight_section import company_insight_section
from insight_tracker.ui.recent_searches_section import recent_searches_section
from insight_tracker.ui.login_section import auth_section
from insight_tracker.ui.settings_section import settings_section
from insight_tracker.ui.side_bar import display_side_bar
from insight_tracker.ui.session_state import initialize_session_state

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
    st.markdown("""
    <style>
    .loading-message {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: #3498db;
        margin-bottom: 20px;
    }
    .loader {
        border: 8px solid #f3f3f3;
        border-top: 8px solid #3498db;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    </style>
    
    <div class="loading-container">
        <div class="loading-message">Preparing Your Insights...</div>
        <div class="loader"></div>
        <div>Please wait while we set up your personalized dashboard.</div>
    </div>
    """, unsafe_allow_html=True)

def handle_auth():
    """Handle authentication process"""
    print("Handling authentication")
    
    if 'code' in st.query_params and st.session_state.user is None:
        print("Handling callback")
        if handle_callback():
            return True
    
    if st.session_state.user is None:
        token = get_cookie()
        if token:
            user_info = validate_token_and_get_user(token)
            if user_info:
                st.session_state.user = user_info
                st.session_state.authentication_status = 'authenticated'
                return True
    
    return st.session_state.user is not None

def check_user_setup_complete(user, user_company) -> bool:
    """
    Check if user has completed their setup
    Returns False if any required data is missing
    """
    if not user:
        return False
    
    # Check if user has role and company set
    if not user[3] or not user[4]:  # user[3] is company, user[4] is role
        return False
    
    # Check if user has company data saved
    if not user_company:
        return False
        
    return True

def display_main_content(user):
    """Display main content based on selected navigation option"""
    user_company = get_user_company_info(user[2])  # user[2] is email
    setup_complete = check_user_setup_complete(user, user_company)
    
    # Set initial navigation based on setup status
    if 'nav_bar_option_selected' not in st.session_state:
        if not setup_complete:
            st.session_state.nav_bar_option_selected = "Settings"
        else:
            st.session_state.nav_bar_option_selected = "Profile Insight"
    
    # Display sidebar and content
    display_side_bar()
    
    if st.session_state.nav_bar_option_selected == "Recent Searches":
        recent_searches_section()
    elif st.session_state.nav_bar_option_selected == "Profile Insight":
        profile_insight_section()
    elif st.session_state.nav_bar_option_selected == "Company Insight":
        company_insight_section()
    elif st.session_state.nav_bar_option_selected == "Settings":
        settings_section(user, user_company, setup_complete)
    elif st.session_state.nav_bar_option_selected == "Logout":
        logout()
    else:
        st.write("Please select an option from the sidebar.")

def main():
    if st.session_state.authentication_status == 'checking':
        show_loading_screen()
        if handle_auth():
            st.session_state.authentication_status = 'authenticated'
            st.rerun()
        else:
            st.session_state.authentication_status = 'unauthenticated'
            st.rerun()
    elif st.session_state.authentication_status == 'authenticated':
        if st.session_state.user is None:
            # If user is None but status is authenticated, something went wrong
            st.session_state.authentication_status = 'unauthenticated'
            st.rerun()
        else:
            user_email = st.session_state.user.get('email')
            user = getUserByEmail(user_email)
            display_main_content(user)
    else:  # unauthenticated
        auth_section()

if __name__ == "__main__":
    main()