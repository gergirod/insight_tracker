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
        
        /* Company Information Card Styling */
        .company-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin: 20px 0;
        }
        
        .company-header {
            display: flex;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .company-name {
            font-size: 1.8rem;
            font-weight: 600;
            color: #1E88E5;
            margin-bottom: 8px;
        }
        
        .company-website {
            color: #666;
            font-size: 1rem;
            margin-top: 4px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .info-item {
            padding: 16px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            transition: all 0.2s ease;
        }
        
        .info-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .info-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .info-value {
            font-size: 1.1rem;
            color: #2c3e50;
            font-weight: 600;
        }
        
        .company-summary {
            background: #f8f9fa;
            padding: 24px;
            border-radius: 12px;
            margin-top: 24px;
            border: 1px solid #e0e0e0;
        }
        
        .summary-header {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1E88E5;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            margin: 4px;
            background: #e3f2fd;
            color: #1E88E5;
            border: 1px solid #bbdefb;
            text-align: center;
        }
        
        /* Make headers blue */
        h3 {
            color: #1E88E5 !important;
            margin-bottom: 1rem !important;
        }
        
        h5 {
            color: #666 !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Add spacing between sections */
        .stMarkdown {
            margin-bottom: 1rem;
        }
        
        /* Card styling */
        .info-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        
        /* Section headers */
        .section-header {
            color: #1E88E5;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section-value {
            color: #2c3e50;
            font-size: 1.2rem;
            font-weight: 500;
        }
        
        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            margin: 4px;
            background: #e3f2fd;
            color: #1E88E5;
            border: 1px solid #bbdefb;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        
        .badge:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Divider */
        .divider {
            height: 1px;
            background: #e0e0e0;
            margin: 1.5rem 0;
        }
        
        /* Link styling */
        .company-link {
            color: #1E88E5;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 12px;
            border-radius: 6px;
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            transition: all 0.2s ease;
        }
        
        .company-link:hover {
            background: #e3f2fd;
            border-color: #bbdefb;
        }
        </style>
    """, unsafe_allow_html=True)

def display_company_data(company):
    # Helper function to handle services display
    def format_services(services):
        if not services:
            return []
        if isinstance(services, str):
            service_list = services.split(',')
        elif isinstance(services, list):
            service_list = services
        else:
            return []
        return [service.strip() for service in service_list]

    # Company Header with improved styling
    st.markdown(f"""
        <div class="info-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2 style="color: #1E88E5; margin: 0;">🏢 {company.company_name or 'N/A'}</h2>
                {f'<a href="{company.company_website}" target="_blank" class="company-link">🌐 Visit Website</a>' if company.company_website else ''}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Company Info Grid with cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="info-card">
                <div class="section-header">🏭 Industry</div>
                <div class="section-value">{}</div>
            </div>
            <div class="info-card">
                <div class="section-header">📍 Headquarters</div>
                <div class="section-value">{}</div>
            </div>
        """.format(
            company.company_industry or 'N/A',
            company.company_headquarters or 'N/A'
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="info-card">
                <div class="section-header">👥 Company Size</div>
                <div class="section-value">{}</div>
            </div>
            <div class="info-card">
                <div class="section-header">📅 Founded</div>
                <div class="section-value">{}</div>
            </div>
        """.format(
            company.company_size or 'N/A',
            company.company_founded_year or 'N/A'
        ), unsafe_allow_html=True)

    # Company Summary
    st.markdown("""
        <div class="info-card">
            <div class="section-header">📝 Company Summary</div>
            <div style="line-height: 1.6; color: #2c3e50;">
                {}
            </div>
        </div>
    """.format(company.company_summary or "No summary available"), unsafe_allow_html=True)

    # Services with improved badge layout
    if services := format_services(company.company_services):
        st.markdown("""
            <div class="info-card">
                <div class="section-header">💼 Services</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">
                    {}
                </div>
            </div>
        """.format(
            ''.join([f'<div class="badge">{service}</div>' for service in services])
        ), unsafe_allow_html=True)

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