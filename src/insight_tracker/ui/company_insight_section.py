import streamlit as st
import pandas as pd
from insight_tracker.db import getUserByEmail, save_company_search, get_recent_company_searches
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.models.requests import CompanyInsightRequest, ProfileInsightRequest
from insight_tracker.api.exceptions.api_exceptions import ApiError

def inject_css():
    st.markdown("""
        <style>
        .small-text {
            font-size: 16px !important;
            line-height: 1.4 !important;
            margin-bottom: 6px;
            color: #555;
        }
        .section-header {
            font-size: 16px !important;
            font-weight: bold;
            margin-top: 20px;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

async def company_insight_section():
    st.header("Company Insight")
    
    user_email = st.session_state.user.get('email')

    # Initialize API client and service
    api_client = InsightApiClient(
        base_url=st.secrets["API_BASE_URL"],
        api_key=st.secrets["API_KEY"],
        openai_api_key=st.secrets["OPENAI_API_KEY"]
    )
    insight_service = InsightService(api_client)

    st.session_state.company_name = st.text_input("Company Name", value=st.session_state.company_name, key="company_name_input")
    st.session_state.industry = st.text_input("Industry", value=st.session_state.industry, key="industry_input")

    col1, col2 = st.columns([1, 1])
    with col1:
        research_button = st.button("Research Company", key="company_research_button")
    with col2:
        st.session_state.research_employees = st.checkbox('Research Employees', value=False)

    if research_button:
        if st.session_state.company_name and st.session_state.industry:
            with st.spinner('Researching company...'):
                try:
                    # Get company insights
                    company_result = await insight_service.get_company_analysis(
                        company_name=st.session_state.company_name,
                        industry=st.session_state.industry,
                        include_employees=st.session_state.research_employees
                    )
                    
                    st.session_state.company_insight_result = company_result
                    st.success("Company research completed!")

                    # Display results
                    display_company_data(company_result.insight)
                    
                    # If employees were requested and available
                    if st.session_state.research_employees and company_result.employees:
                        st.session_state.employee_profiles = []
                        with st.spinner("Researching employees..."):
                            for employee in company_result.employees:
                                try:
                                    profile_result = await insight_service.get_profile_analysis(
                                        full_name=employee,
                                        company_name=st.session_state.company_name
                                    )
                                    st.session_state.employee_profiles.append(profile_result.profile)
                                except ApiError as e:
                                    st.warning(f"Couldn't fetch profile for {employee}: {e.error_message}")
                        
                        if st.session_state.employee_profiles:
                            display_people_data()

                    # Add save button
                    if st.button("Save Search", key="save_company_search"):
                        save_company_search(user_email, company_result.insight)
                        st.success("Search saved successfully!")

                except ApiError as e:
                    st.error(f"API Error: {e.error_message}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please provide both Company Name and Industry.")

def display_company_data(company):
    inject_css()
    st.markdown("<h2>🏢 Company Information</h2>", unsafe_allow_html=True)
    
    # Convert company data to DataFrame
    company_dict = {
        'Name': company.company_name,
        'Website': company.company_website,
        'LinkedIn': company.company_linkedin,
        'Industry': company.company_industry,
        'Size': company.company_size,
        'Summary': company.company_summary
    }
    st.session_state.company_data_frame = pd.DataFrame([company_dict])
    st.dataframe(st.session_state.company_data_frame)

    # Display detailed information
    company_fields = {
        "🏷️ Company Name": company.company_name,
        "🌐 Website": company.company_website,
        "📝 Summary": company.company_summary,
        "🏭 Industry": company.company_industry,
        "👥 Size": company.company_size,
        "🛠️ Services": ', '.join(company.company_services) if company.company_services else None,
        "🏢 Industries": ', '.join(company.company_industries) if company.company_industries else None,
        "🏆 Awards": ', '.join(company.company_awards_recognitions) if company.company_awards_recognitions else None,
        "🤝 Clients": ', '.join(company.company_clients_partners) if company.company_clients_partners else None,
        "📍 Headquarters": company.company_headquarters,
        "📅 Founded": company.company_founded_year
    }

    for label, value in company_fields.items():
        if value:
            st.markdown(
                f"<p class='section-header'>{label}:</p><p class='small-text'>{value}</p>",
                unsafe_allow_html=True
            )

def display_people_data():
    if not st.session_state.employee_profiles:
        return

    view_option = st.radio(
        "Select View",
        options=["List View", "Table View"],
        index=0
    )

    st.markdown("### 👥 Employee Profiles")

    if view_option == "Table View":
        # Convert profiles to DataFrame
        profiles_data = []
        for profile in st.session_state.employee_profiles:
            profiles_data.append({
                'Name': profile.full_name,
                'Title': profile.current_job_title,
                'Background': profile.professional_background,
                'Contact': profile.contact,
                'LinkedIn': profile.linkedin_url
            })
        st.dataframe(pd.DataFrame(profiles_data))
    else:
        for profile in st.session_state.employee_profiles:
            with st.expander(f"📋 {profile.full_name}"):
                if profile.current_job_title:
                    st.markdown(f"**Current Title:** {profile.current_job_title}")
                if profile.professional_background:
                    st.markdown(f"**Background:** {profile.professional_background}")
                if profile.past_jobs:
                    st.markdown(f"**Past Jobs:** {profile.past_jobs}")
                if profile.key_achievements:
                    st.markdown(f"**Key Achievements:** {profile.key_achievements}")
                if profile.contact:
                    st.markdown(f"**Contact:** {profile.contact}")
                if profile.linkedin_url:
                    st.markdown(f"**LinkedIn:** [{profile.linkedin_url}]({profile.linkedin_url})")

# Add this to handle async operations with Streamlit
def init():
    import asyncio
    if "company_insight_section" not in st.session_state:
        st.session_state.company_insight_section = asyncio.new_event_loop()

    loop = st.session_state.company_insight_section
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(company_insight_section())