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

def display_company_data(company):
    st.markdown("<h2>🏢 Company Information</h2>", unsafe_allow_html=True)
    
    cols = st.columns(2)  # Create two columns for layout

    with cols[0]:
        st.markdown(f"**🏷️ Company Name:** {company.company_name}")
        st.markdown(f"**🌐 Website:** {company.company_website or 'N/A'}")
        st.markdown(f"**🔗 LinkedIn:** [{company.company_linkedin}]({company.company_linkedin})" if company.company_linkedin else "N/A")
        st.markdown(f"**📝 Summary:** {company.company_summary or 'N/A'}")
        st.markdown(f"**🏭 Industry:** {company.company_industry or 'N/A'}")
        st.markdown(f"**👥 Size:** {company.company_size or 'N/A'}")

    with cols[1]:
        st.markdown(f"**🛠️ Services:** {', '.join(company.company_services) if company.company_services else 'N/A'}")
        st.markdown(f"**🏢 Industries:** {', '.join(company.company_industries) if company.company_industries else 'N/A'}")
        st.markdown(f"**🏆 Awards:** {', '.join(company.company_awards_recognitions) if company.company_awards_recognitions else 'N/A'}")
        st.markdown(f"**🤝 Clients:** {', '.join(company.company_clients_partners) if company.company_clients_partners else 'N/A'}")
        st.markdown(f"**📍 Headquarters:** {company.company_headquarters or 'N/A'}")
        st.markdown(f"**📅 Founded:** {company.company_founded_year or 'N/A'}")
        st.markdown(f"**🌱 Culture:** {', '.join(company.company_culture) if company.company_culture else 'N/A'}")
        st.markdown(f"**📰 Recent Updates:** {', '.join(company.company_recent_updates) if company.company_recent_updates else 'N/A'}")

def settings_section(user, user_company, setup_complete=True):
    """Display and handle settings section"""
    
    if not setup_complete:
        st.markdown("""
            <div style="padding: 2rem; background-color: #f8f9fa; border-radius: 0.5rem; margin: 1rem 0;">
                <h2 style="color: #1E88E5;">🎯 Complete Your Profile Setup</h2>
                <p style="font-size: 1.1rem; margin: 1rem 0;">
                    Welcome to Insight Tracker! Please complete your profile setup to access all features.
                </p>
                <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                    <h3 style="color: #2C3E50; margin-top: 0;">Why this matters:</h3>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li style="margin: 0.5rem 0;">✨ <strong>Personalized AI Content:</strong> Get tailored insights</li>
                        <li style="margin: 0.5rem 0;">🎯 <strong>Better Fit Evaluations:</strong> More accurate matches</li>
                        <li style="margin: 0.5rem 0;">📧 <strong>Smarter Outreach:</strong> More relevant communications</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Personal Information Section
    st.markdown("""
        <div style="padding: 20px; background-color: white; border-radius: 10px; border: 1px solid #eee; margin-bottom: 30px;">
            <h3 style="color: #1E88E5; margin-bottom: 20px;">👤 Personal Information</h3>
            <p style="color: #666; margin-bottom: 20px;">
                Update your basic profile information below. This information helps personalize your experience.
            </p>
        </div>
    """, unsafe_allow_html=True)

    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )
    
    full_name_value = user[1] if user is not None else ""
    contact_info = user[2] if user is not None else ""
    role_position_value = user[3] if user is not None else ""
    company_value = user[4] if user is not None else ""

    full_name = st.text_input("Full Name", placeholder="Enter your full name", value=full_name_value)
    email = st.text_input("Email", value=contact_info, disabled=True)
    role_position = st.text_input("Role/Position", placeholder="Enter your role or position", value=role_position_value)
    company = st.text_input("Company", placeholder="Enter your company name", value=company_value)

    if st.button("💾 Save Personal Information", key="save_button", help="Save your personal profile information"):
        email = st.session_state.user.get('email')
        create_user_if_not_exists(full_name, email, role_position, company)
        st.success("✅ Personal information saved successfully!")
        
    # Company Information Section
    st.markdown("""
        <div style="padding: 20px; background-color: white; border-radius: 10px; border: 1px solid #eee; margin: 30px 0;">
            <h3 style="color: #1E88E5; margin-bottom: 20px;">🏢 Company Information</h3>
            <p style="color: #666; margin-bottom: 20px;">
                Fetch and save detailed information about your company. This helps provide more accurate insights and recommendations.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Method selection with better explanation
    st.markdown("""
        <p style="color: #666; margin-bottom: 10px;">
            Choose how you want to fetch your company data:
        </p>
    """, unsafe_allow_html=True)
    
    search_method = st.radio(
        "Select data fetch method:",
        options=["By URL", "By Name and Industry"],
        help="Choose the most convenient way to fetch your company information",
        index=0
    )

    if search_method == "By URL":
        company_url = st.text_input(
            "Company URL", 
            placeholder="Enter the company URL (e.g., https://company.com)",
            help="Enter your company's website URL to fetch detailed information"
        )
    else:
        company_name = st.text_input(
            "Company Name",
            placeholder="Enter the company's full name",
            help="Enter your company's official name"
        )
        company_industry = st.text_input(
            "Industry",
            placeholder="Enter the company's primary industry",
            help="Enter the main industry your company operates in"
        )

    # Fetch and Save Company Data
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Fetch Company Data", key="fetch_company_data_button"):
            insight_service = InsightService(api_client)
            try:
                with st.spinner('Fetching company data...'):
                    if search_method == "By URL" and company_url:
                        company_result = run_async(
                            insight_service.get_company_analysis_by_url(company_url=company_url)
                        )
                    elif search_method == "By Name and Industry" and company_name and company_industry:
                        company_result = run_async(
                            insight_service.get_company_analysis(
                                company_name=company_name,
                                industry=company_industry
                            )
                        )
                    else:
                        st.warning("Please provide the required information based on the selected method.")
                        return

                    st.session_state.company_result = company_result
                    st.success("✅ Company data fetched successfully!")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

    with col2:
        if st.button("💾 Save Company Data", 
                    key="save_company_data_button",
                    help="Save the fetched company information to your profile"):
            if 'company_result' in st.session_state:
                save_user_company_info(email, st.session_state.company_result.company)
                st.success("✅ Company data saved successfully!")
            else:
                st.warning("ℹ️ No company data to save. Please fetch company data first.")

    # Display existing company data if available
    if user_company is not None or 'company_result' in st.session_state:
        st.markdown("""
            <div style="padding: 20px; background-color: white; border-radius: 10px; border: 1px solid #eee; margin: 30px 0;">
                <h3 style="color: #1E88E5;">📋 Current Company Information</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if 'company_result' in st.session_state:
            display_company_data(st.session_state.company_result.company)
        elif user_company is not None:
            display_company_data(user_company)