import streamlit as st
from streamlit_option_menu import option_menu

def display_side_bar():
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
            st.session_state.nav_bar_option_selected = option_menu(
                menu_title="Insight Tracker",
                options=["Profile Insight", "Company Insight", "Recent Searches", "Settings", "Logout"],
                default_index=0,
                key="navigation_menu",
                styles={
                    "container": {"padding": "0!important", "background-color": "#ffffff"},
                    "icon": {"color": "#495057", "font-size": "16px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "padding": "15px",
                        "margin": "0px",
                        "--hover-color": "#f8f9fa"
                    },
                    "nav-link-selected": {
                        "background-color": "#e7f1ff",
                        "color": "#0d6efd",
                    },
                    "menu-title": {
                        "padding": "15px",
                        "font-size": "18px",
                        "font-weight": "600"
                    }
                }
            )