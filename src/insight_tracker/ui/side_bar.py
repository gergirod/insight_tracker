import streamlit as st
from streamlit_option_menu import option_menu
from insight_tracker.utils.logger import logger

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

    # Debug logging
    logger.info(f"Displaying sidebar. User in session: {st.session_state.get('user') is not None}")
    logger.info(f"Current nav option: {st.session_state.get('nav_bar_option_selected')}")

    # -------------------- Sidebar Navigation -------------------- #
    with st.sidebar:
        # Debug info in sidebar
        st.write(f"Debug - Auth Status: {st.session_state.get('authentication_status')}")
        st.write(f"Debug - User exists: {st.session_state.get('user') is not None}")
        
        if st.session_state.get('user') is not None:
            try:
                options = ["Profile Insight", "Company Insight", "Recent Searches", "Settings", "Logout"]
                current_idx = options.index(st.session_state.nav_bar_option_selected) if st.session_state.nav_bar_option_selected in options else 0
                
                logger.info(f"Attempting to display option_menu with index {current_idx}")
                
                selected = option_menu(
                    menu_title="Insight Tracker",
                    options=options,
                    icons=["person-lines-fill", "building", "clock-history", "gear", "box-arrow-right"],
                    default_index=current_idx,
                    key="navigation",
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
                
                logger.info(f"Option menu displayed successfully, selected: {selected}")
                
                # Update session state if selection changed
                if selected != st.session_state.nav_bar_option_selected:
                    st.session_state.nav_bar_option_selected = selected
                    st.rerun()
                    
                return selected
            except Exception as e:
                logger.error(f"Error displaying sidebar menu: {e}")
                st.error("Error displaying navigation menu")
        else:
            logger.warning("No user in session state, skipping sidebar menu")

    return st.session_state.nav_bar_option_selected