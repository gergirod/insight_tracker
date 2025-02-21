import streamlit as st
from streamlit_option_menu import option_menu
from insight_tracker.utils.logger import logger

def display_side_bar():
    """Display the sidebar navigation"""
    with st.sidebar:
        if st.session_state.get('user') is not None:
            try:
                # Get current index
                options = ["Profile Insight", "Company Insight", "Recent Searches", "Settings", "Logout"]
                current_idx = options.index(st.session_state.nav_bar_option_selected) if st.session_state.nav_bar_option_selected in options else 0
                
                logger.info(f"Attempting to display menu with index {current_idx}")
                
                selected = option_menu(
                    "Insight Tracker",
                    options,
                    icons=['person', 'building', 'clock-history', 'gear', 'box-arrow-right'],
                    default_index=current_idx,
                )
                
                logger.info(f"Menu displayed, selected: {selected}")
                
                if selected != st.session_state.nav_bar_option_selected:
                    st.session_state.nav_bar_option_selected = selected
                    st.rerun()
                
                return selected
                
            except Exception as e:
                logger.error(f"Error in sidebar: {e}")
                st.error("Navigation menu error")

    return st.session_state.nav_bar_option_selected