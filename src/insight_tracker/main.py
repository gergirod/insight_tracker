#!/usr/bin/env python
#!/usr/bin/env python
import sys
import asyncio
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from insight_tracker.auth import login, handle_callback, signup

# Import your custom modules
from insight_tracker.profile_crew import InsightTrackerCrew
from insight_tracker.company_crew import CompanyInsightTrackerCrew
from insight_tracker.company_person_crew import CompanyPersonInsightTrackerCrew
from insight_tracker.company_crew import Company
from insight_tracker.company_person_crew import Profile
from insight_tracker.profile_crew import ProfessionalProfile
from insight_tracker.db import create_user_if_not_exists, getUserByEmail
from insight_tracker.db import init_db
from insight_tracker.ui.profile_insight_section import profile_insight_section
from insight_tracker.utils.util import convert_urls_to_dicts, run_company_person_crew
from insight_tracker.ui.session_state import initialize_session_state
from insight_tracker.ui.company_insight_section import company_insight_section
from insight_tracker.ui.login_section import auth_section
from insight_tracker.ui.settings_section import settings_section
from insight_tracker.ui.side_bar import display_side_bar
# -------------------- Session State Initialization -------------------- #

initialize_session_state()
init_db()

    

# -------------------- Main Application Flow -------------------- #
def main():
    if 'code' in st.query_params and st.session_state.user is None:
        handle_callback()
    # Check if the user is logged in
    if st.session_state.user is None :
        auth_section()
    else:
        user_email = st.session_state.user.get('email')
        user = getUserByEmail(user_email)
        display_side_bar()
        # Your existing main application logic goes here
        if st.session_state.nav_bar_option_selected == "Profile Insight":
            profile_insight_section()
        elif st.session_state.nav_bar_option_selected == "Company Insight":
            company_insight_section()
        elif st.session_state.nav_bar_option_selected == "Settings":
            settings_section(user)
        elif st.session_state.nav_bar_option_selected == "Logout":
            del st.session_state['user']
            st.rerun()
        else:
            st.write("Please select an option from the sidebar.")


if __name__ == "__main__":
    main()


def run():
    """
    Run the crew.
    """
    inputs = {
        'profile': '',
        'company': ''
    }
    InsightTrackerCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'profile': '',
        'company': ''
    }
    try:
        InsightTrackerCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        InsightTrackerCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
