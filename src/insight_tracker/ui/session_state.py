import streamlit as st
from insight_tracker.utils.cookie_manager import load_auth_cookie

def initialize_session_state():
    """Initialize all session state variables"""
    
    # Authentication related
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = 'unauthenticated'
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'id_token' not in st.session_state:
        st.session_state.id_token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_new_user' not in st.session_state:
        st.session_state.is_new_user = False
        
    # Navigation related
    if 'nav_bar_option_selected' not in st.session_state:
        st.session_state.nav_bar_option_selected = "Profile Insight"
        
    # Search related
    if 'search_method' not in st.session_state:
        st.session_state.search_method = "Search by Name and Industry"
    if 'company_name' not in st.session_state:
        st.session_state.company_name = ""
    if 'industry' not in st.session_state:
        st.session_state.industry = ""
    if 'person_name' not in st.session_state:
        st.session_state.person_name = ""
    if 'person_company' not in st.session_state:
        st.session_state.person_company = ""
        
    # Data storage
    if 'company_data' not in st.session_state:
        st.session_state.company_data = None
    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = None
    if 'user_company' not in st.session_state:
        st.session_state.user_company = None
        
    # UI state
    if 'company_research_trigger' not in st.session_state:
        st.session_state.company_research_trigger = False
    if 'profile_research_trigger' not in st.session_state:
        st.session_state.profile_research_trigger = False
    if 'research_employees' not in st.session_state:
        st.session_state.research_employees = False

    # Only initialize if not already set
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        
        # Don't override existing authentication status
        if 'authentication_status' not in st.session_state:
            if load_auth_cookie():
                st.session_state.authentication_status = 'authenticated'
            else:
                st.session_state.authentication_status = 'unauthenticated'
                st.session_state.access_token = None
                st.session_state.user = None

        # Initialize other session state variables if they don't exist
        defaults = {
            'is_new_user': False,
            'nav_bar_option_selected': 'Profile Insight',
            'user_company': None,
            'company_data': None,
            'profile_data': None,
            'person_name': '',
            'person_company': '',
            'company_name': '',
            'industry': '',
            'people_list': [],
            'result_company': None,
            'company_task_running': False,
            'company_task_completed': False,
            'pydantic_url_list': [],
            'url_list_dict': [],
            'current_view': 'List View',
            'final_crew_result': [],
            'company_insight_tracker_result': None,
            'persons_data_frame': None,
            'company_data_frame': None,
            'company_inputs': {},
            'person_inputs': {},
            'profile_research_trigger': False,
            'company_research_trigger': False,
            'name': None,
            'research_employees': False,
            'token': None,
            'handling_callback': False,
            'search_method': 'Search by Name and Industry',
            'fit_result': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value