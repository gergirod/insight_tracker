import streamlit as st

def initialize_session_state():
    default_values = {
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
        'nav_bar_option_selected': 'Profile Insight',
        'profile_research_trigger': False,
        'company_research_trigger': False,
        'user': None,
        'user_company': None,
        'name': None,
        'research_employees': False,
        'token': None,
        'handling_callback': False,
        'authentication_status': 'checking',
        'company_data': None,
        'profile_data': None,
        'search_method': 'Search by Name and Industry',
        'fit_result': None,
        'last_auth_check': 0,
        'user_info': None,
        'auth_attempt_count': 0,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value