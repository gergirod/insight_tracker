import streamlit as st

def initialize_session_state():
    """Initialize session state variables"""
    if 'authentication_status' not in st.session_state:
        # Try to load from cookie first
        if load_auth_cookie():
            st.session_state.authentication_status = 'authenticated'
        else:
            st.session_state.authentication_status = 'unauthenticated'
    
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
        
    if 'user' not in st.session_state:
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