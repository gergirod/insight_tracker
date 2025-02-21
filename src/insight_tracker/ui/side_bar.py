import streamlit as st
from insight_tracker.utils.logger import logger

def display_side_bar():
    """Display the sidebar navigation"""
    # Custom CSS for cleaner buttons
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] p {
            font-size: 16px;
            padding: 8px 0;
            margin: 0;
        }
        
        div.stButton > button {
            width: 100%;
            text-align: left;
            background: none;
            border: none;
            padding: 12px 16px;
            font-size: 15px;
            color: #495057;
        }
        
        div.stButton > button:hover {
            background-color: #f8f9fa;
            color: #0d6efd;
        }
        
        div.stButton > button[data-selected="true"] {
            background-color: #e7f1ff;
            color: #0d6efd;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.session_state.get('user') is not None:
            st.markdown("### Insight Tracker")
            st.markdown("---")
            
            # Navigation options with icons
            options = {
                "Profile Insight": "👤",
                "Company Insight": "🏢",
                "Recent Searches": "🕒",
                "Settings": "⚙️",
                "Logout": "🚪"
            }
            
            current_option = st.session_state.get('nav_bar_option_selected', 'Profile Insight')
            
            for option, icon in options.items():
                # Add selected state styling
                is_selected = current_option == option
                button_style = "background-color: #e7f1ff;" if is_selected else ""
                
                # Create button with icon
                if st.button(
                    f"{icon} {option}",
                    key=f"nav_{option.lower().replace(' ', '_')}",
                    help=f"Go to {option}"
                ):
                    st.session_state.nav_bar_option_selected = option
                    st.rerun()

    return st.session_state.nav_bar_option_selected