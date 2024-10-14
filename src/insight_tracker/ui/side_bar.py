import streamlit as st
from streamlit_option_menu import option_menu

def display_side_bar():
    # -------------------- Sidebar Navigation -------------------- #
    with st.sidebar:
        if st.session_state.user is not None:
            st.session_state.nav_bar_option_selected = option_menu(
                menu_title="Insight Tracker",
                options=["Profile Insight", "Company Insight", "Settings", "Logout"],
                default_index=0,
                key="navigation_menu"
            )