import streamlit as st
from insight_tracker.db import create_user_if_not_exists, save_user_company_info
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.exceptions.api_exceptions import ApiError
import os
import asyncio
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_async(coroutine):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def inject_css():
    st.markdown("""
        <style>
        /* Base button style for all action buttons */
        .stButton > button {
            background-color: #4f46e5 !important;  /* Indigo color */
            color: white !important;
            padding: 14px 24px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            text-decoration: none !important;
            border-radius: 50px !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2) !important;
            transition: all 0.2s ease !important;
            margin: 10px 0 !important;
            letter-spacing: 0.3px !important;
            text-align: center !important;
            width: 100% !important;
        }

        /* Hover state for all buttons */
        .stButton > button:hover {
            background-color: #4338ca !important;  /* Darker indigo */
            box-shadow: 0 4px 6px rgba(79, 70, 229, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Active state */
        .stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* Disabled state */
        .stButton > button:disabled {
            background-color: #6c757d !important;
            opacity: 0.65 !important;
            cursor: not-allowed !important;
        }

        /* Save button style - keeping green but matching the new style */
        .stButton > button:has(div:contains("Save")),
        .stButton > button:has(div:contains("Update")) {
            background-color: #28a745 !important;
            box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2) !important;
        }

        .stButton > button:has(div:contains("Save")):hover,
        .stButton > button:has(div:contains("Update")):hover {
            background-color: #218838 !important;
            box-shadow: 0 4px 6px rgba(40, 167, 69, 0.3) !important;
        }

        /* Ensure text color stays white */
        .stButton > button div {
            color: white !important;
        }

        /* Input field styling */
        .stTextInput > div > div {
            border-radius: 4px !important;
        }

        /* Add spacing between input fields */
        .stTextInput {
            margin-bottom: 0.5rem !important;
        }

        /* Ensure consistent button styling */
        [data-testid="stButton"] > button {
            background-color: #0d6efd !important;  /* Bootstrap blue */
            color: white !important;
        }

        [data-testid="stButton"] > button:hover {
            background-color: #0b5ed7 !important;  /* Darker blue */
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def display_company_data(company):
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏢 Company Information</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="company-data-grid">', unsafe_allow_html=True)
    
    # Company Basic Info
    data_items = [
        ("Company Name", company.company_name, "🏷️"),
        ("Website", company.company_website or "N/A", "🌐"),
        ("Industry", company.company_industry or "N/A", "🏭"),
        ("Size", company.company_size or "N/A", "👥"),
        ("Headquarters", company.company_headquarters or "N/A", "📍"),
        ("Founded", company.company_founded_year or "N/A", "📅")
    ]
    
    for label, value, icon in data_items:
        st.markdown(f"""
            <div class="data-item">
                <div class="data-label">{icon} {label}</div>
                <div class="data-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Company Details
    if company.company_summary:
        st.markdown("""
            <div class="data-item" style="grid-column: 1 / -1;">
                <div class="data-label">📝 Company Summary</div>
                <div class="data-value">{}</div>
            </div>
        """.format(company.company_summary), unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def settings_section(user, user_company, setup_complete=True):
    inject_css()
    
    # Personal Information Section
    st.markdown("""
        <div style="margin-bottom: 32px;">
            <h2 style="
                color: #1E88E5;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                👤 Personal Information
            </h2>
            <p style="
                color: #666;
                margin-bottom: 24px;
                font-size: 0.95rem;
            ">
                Update your professional details to enhance your outreach effectiveness. 
                This information helps us provide personalized insights for building meaningful connections 
                and crafting more impactful communications.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Form inputs
    full_name_value = user[1] if user is not None else ""
    contact_info = user[2] if user is not None else ""
    role_position_value = user[3] if user is not None else ""
    company_value = user[4] if user is not None else ""

    full_name = st.text_input("Full Name", placeholder="Enter your full name", value=full_name_value)
    email = st.text_input("Email", value=contact_info, disabled=True)
    role_position = st.text_input("Role/Position", placeholder="Enter your role or position", value=role_position_value)
    company = st.text_input("Company", placeholder="Enter your company name", value=company_value)

    # Add some space before the button
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Personal Information Save Button - Full width
    if st.button("💾 Save Personal Information", 
                key="save_personal_info",
                use_container_width=True):
        email = st.session_state.user.get('email')
        create_user_if_not_exists(full_name, email, role_position, company)
        st.success("✅ Personal information saved successfully!")

    # Add spacing between sections
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    # Company Information Section - matching style with Personal Information
    st.markdown("""
        <div style="margin-bottom: 32px;">
            <h2 style="
                color: #1E88E5;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                🏢 Company Information
            </h2>
            <p style="
                color: #666;
                margin-bottom: 24px;
                font-size: 0.95rem;
            ">
                Help us understand your company context to provide better insights for your professional outreach 
                and strategic connections.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Simplified company data input
    company_url = st.text_input(
        "Company Website",
        placeholder="Enter your company's website (e.g., https://company.com)",
        help="We'll use this to fetch detailed information about your company"
    )

    # Company Information Update Button - Full width
    if st.button("🔄 Update Company Information",
                key="update_company_info",
                use_container_width=True):
        try:
            with st.spinner('Analyzing company data...'):
                api_client = InsightApiClient(
                    base_url=os.getenv('API_BASE_URL'),
                    api_key=os.getenv('API_KEY'),
                    openai_api_key=os.getenv('OPENAI_API_KEY'),
                    verify_ssl=False
                )
                insight_service = InsightService(api_client=api_client)
                company_result = run_async(
                    insight_service.get_company_analysis_by_url(company_url=company_url)
                )
                
                if company_result and company_result.company:
                    save_user_company_info(email, company_result.company)
                    st.session_state.company_result = company_result
                    st.success("✅ Company information updated successfully!")
                else:
                    st.error("❌ Couldn't fetch company information. Please check the URL and try again.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

    # Display current company information if available
    if user_company is not None or 'company_result' in st.session_state:
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        if 'company_result' in st.session_state:
            display_company_data(st.session_state.company_result.company)
        elif user_company is not None:
            display_company_data(user_company)

    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )