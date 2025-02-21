import streamlit as st
from streamlit_option_menu import option_menu
from insight_tracker.utils.logger import logger

def display_side_bar():
    """Display the sidebar navigation"""
    # Custom CSS for minimalistic design
    st.markdown("""
        <style>
        /* Clean up sidebar spacing */
        section[data-testid="stSidebar"] {
            padding-top: 2rem;
            background-color: #f8f9fa;
        }
        
        /* Style links */
        .nav-link {
            padding: 16px 20px;
            border-radius: 4px;
            margin: 4px 0;
            display: flex;
            align-items: center;
            font-size: 15px;
            font-weight: 400;
            color: #495057;
            background: none;
            border: none;
            transition: all 0.2s ease;
        }
        
        /* Active link */
        .nav-link.active {
            background-color: #e7f1ff !important;
            color: #0d6efd !important;
            font-weight: 500;
        }
        
        /* Hover state */
        .nav-link:hover {
            background-color: #f1f3f5;
            color: #0d6efd;
        }
        
        /* Menu title */
        .nav-title {
            font-size: 18px;
            font-weight: 600;
            color: #212529;
            padding: 0 20px 20px 20px;
            margin-bottom: 0;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.session_state.get('user') is not None:
            selected = option_menu(
                menu_title="Insight Tracker",
                options=["Profile Insight", "Company Insight", "Recent Searches", "Settings", "Logout"],
                icons=["person", "building", "clock-history", "gear", "box-arrow-right"],
                menu_icon="graph-up",
                default_index=0,
                styles={
                    "container": {"padding": "0"},
                    "icon": {"font-size": "16px", "margin-right": "8px"},
                    "nav-link": {
                        "font-size": "15px",
                        "text-align": "left",
                        "padding": "16px 20px",
                        "margin": "4px 0",
                    },
                    "menu-title": {
                        "padding": "0 20px 20px 20px",
                        "font-size": "18px",
                        "font-weight": "600"
                    }
                }
            )
            
            if selected != st.session_state.nav_bar_option_selected:
                st.session_state.nav_bar_option_selected = selected
                st.rerun()

    return st.session_state.nav_bar_option_selected