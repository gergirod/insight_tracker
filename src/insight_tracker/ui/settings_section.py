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

def inject_settings_css():
    st.markdown("""
        <style>
        /* Button styling */
        .stButton > button {
            width: 100%;
            background-color: rgb(49, 132, 252) !important;  /* Updated to match app theme */
            color: white !important;
            padding: 0.5rem 1rem !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            border: none !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            background-color: rgb(28, 119, 252) !important;  /* Slightly darker on hover */
            box-shadow: 0 2px 6px rgba(49, 132, 252, 0.2) !important;
        }
        
        .stButton > button:active {
            transform: translateY(1px);
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
        ("Company Services", company.company_services or "N/A", "💼"),
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
    inject_settings_css()
    
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
    
    # Personal Information save button
    st.markdown("""
        <style>
        [data-testid="stButton"] > button {
            background-color: rgb(49, 132, 252);
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("Save", 
                key="save_button",
                use_container_width=True,
                help="Save your personal profile information"):
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

    # Single button for fetch and save
    if st.button(
        "Update Company Information",
        key="update_company_data",
        use_container_width=True,
        help="Fetch and save your company information"
    ):
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
        print(user_company)
        if user_company is not None:
            display_company_data(user_company)

    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )