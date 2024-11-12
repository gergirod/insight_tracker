import streamlit as st
from insight_tracker.db import create_user_if_not_exists

def inject_settings_css():
    st.markdown("""
        <style>
        .small-text {
            font-size: 14px;
            color: #4f4f4f;
            line-height: 1.5;
            margin-bottom: 8px;
        }
        
        .section-header {
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            margin-top: 10px;
            margin-bottom: 2px;
        }
        
        .container {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            background-color: #fafafa;
        }

        /* Input field styling */
        .stTextInput > div > div {
            border-radius: 8px;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            background-color: #007bff;
            color: white !important;
            border: none;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover,
        .stButton > button:active,
        .stButton > button:focus {
            background-color: #0056b3;
            border: none;
            color: white !important;
        }
        
        /* Save button specific styling */
        .stButton > button:has(div:contains("Save")) {
            background-color: #28a745;
        }
        
        .stButton > button:has(div:contains("Save")):hover,
        .stButton > button:has(div:contains("Save")):active,
        .stButton > button:has(div:contains("Save")):focus {
            background-color: #218838;
            color: white !important;
        }

        /* Ensure button text stays white in all states */
        .stButton > button > div {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def settings_section(user):
    st.header("Settings")

    inject_settings_css()  # Inject CSS for styling

    full_name_value = user[1] if user is not None else ""
    contact_info = user[2] if user is not None else ""
    role_position_value = user[3] if user is not None else ""
    company_value = user[4] if user is not None else ""
    # Input fields for the user settings
    full_name = st.text_input("Full Name", placeholder="Enter your full name", value= full_name_value)
    email = st.text_input("Email", value=contact_info, disabled=True)
    role_position = st.text_input("Role/Position", placeholder="Enter your role or position", value= role_position_value)
    company = st.text_input("Company", placeholder="Enter your company name", value= company_value)
    #company_url = st.text_input("Company URL", placeholder="Enter the company URL for scraping")
    # Layout for the buttons
    col1, col2 = st.columns([1, 1])

    # Save button
    with col1:
        if st.button("Save", key="save_button"):
            # Simulate saving the data (this could be saving to a database or file)
            st.success(f"Settings saved! \nName: {full_name} \nRole: {role_position} \nCompany: {company}")
            # Store the settings in session state (this allows you to reuse the settings elsewhere in the app)
            st.session_state['full_name'] = full_name
            st.session_state['role_position'] = role_position
            st.session_state['company'] = company

            email = st.session_state.user.get('email')
            create_user_if_not_exists(full_name, email, role_position, company)