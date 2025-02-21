import streamlit as st
from streamlit_option_menu import option_menu

def display_side_bar():
    """Display the sidebar navigation"""
    # Custom CSS for the sidebar
    st.markdown("""
        <style>
        /* Option menu styling */
        .nav-link {
            color: #495057 !important;
            background-color: transparent !important;
        }
        
        .nav-link:hover {
            color: #0d6efd !important;
            background-color: #f8f9fa !important;
        }
        
        .nav-link.active {
            color: #0d6efd !important;
            background-color: #e7f1ff !important;
            font-weight: 500;
        }
        
        /* Menu title styling */
        .nav-link-title {
            color: #212529 !important;
            font-weight: 600 !important;
        }
        
        /* Container styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

    # -------------------- Sidebar Navigation -------------------- #
    with st.sidebar:
        if st.session_state.user is not None:
            # Add a unique key to the selectbox
            selected = st.selectbox(
                "Navigation",
                ["Profile Insight", "Company Insight", "Recent Searches", "Settings", "Logout"],
                key="nav_sidebar_select"  # Add unique key
            )
            
            # Only update if selection changed
            if selected != st.session_state.nav_bar_option_selected:
                st.session_state.nav_bar_option_selected = selected
                # Force a rerun to reflect the new selection
                st.rerun()

    return st.session_state.nav_bar_option_selected