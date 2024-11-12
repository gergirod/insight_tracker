import streamlit as st
import pandas as pd
from insight_tracker.db import getUserByEmail, save_company_search, get_recent_company_searches
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.models.requests import CompanyInsightRequest, ProfileInsightRequest
from insight_tracker.api.exceptions.api_exceptions import ApiError
from insight_tracker.api.models.responses import Company
import asyncio
import os

def inject_css():
    st.markdown("""
        <style>
        /* Modern Radio Button Styling */
        .stRadio > label {
            display: none;  /* Hide the default label */
        }
        
        .stRadio > div {
            display: flex;
            gap: 15px;
            margin-top: 1rem;
            margin-bottom: 2rem;
        }
        
        /* Hide the default radio button circle */
        .stRadio input[type="radio"] {
            display: none !important;
        }
        
        .stRadio > div > div {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px 25px;
            cursor: pointer;
            transition: all 0.2s ease;
            flex: 1;
            text-align: center;
            color: #495057;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stRadio > div > div:hover {
            background-color: #f8f9fa;
            border-color: #0d6efd;
            color: #0d6efd;
        }
        
        .stRadio > div > div[data-value="true"] {
            background-color: #e7f1ff;
            color: #0d6efd;
            border-color: #0d6efd;
            font-weight: 500;
        }

        /* View selector specific styling */
        div[data-testid="stHorizontalBlock"] .stRadio > div {
            gap: 10px;
        }

        div[data-testid="stHorizontalBlock"] .stRadio > div > div {
            padding: 10px 20px;
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
        .stButton > button:has(div:contains("💾")) {
            background-color: #28a745;
        }
        
        .stButton > button:has(div:contains("💾")):hover,
        .stButton > button:has(div:contains("💾")):active,
        .stButton > button:has(div:contains("💾")):focus {
            background-color: #218838;
            color: white !important;
        }
        
        /* Checkbox styling */
        .stCheckbox > label {
            color: #495057;
        }
        
        .stCheckbox > div > div > div {
            background-color: #007bff;
        }

        /* Ensure button text stays white in all states */
        .stButton > button > div {
            color: white !important;
        }

        /* Search Method Radio Button Styling */
        div[data-testid="stRadio"] > div {
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        }
        
        div[data-testid="stRadio"] > div > div > div {
            background-color: white;
            border: 1px solid #e9ecef;
            padding: 10px 20px;
            border-radius: 8px;
            color: #495057;
            font-weight: 400;
            transition: all 0.2s ease;
        }
        
        div[data-testid="stRadio"] > div > div > div:hover {
            background-color: #f8f9fa;
            border-color: #0d6efd;
            color: #0d6efd;
        }
        
        div[data-testid="stRadio"] > div > div > div[aria-checked="true"] {
            background-color: #e7f1ff;
            color: #0d6efd;
            border-color: #0d6efd;
            font-weight: 500;
        }
        
        /* Hide the default radio button */
        div[data-testid="stRadio"] input[type="radio"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

def run_async(coroutine):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def company_insight_section():
    inject_css()
    st.header("Company Insight")
    
    user_email = st.session_state.user.get('email')

    # Initialize API client and service
    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )
    insight_service = InsightService(api_client)

    # Ensure search_method is in session state
    if 'search_method' not in st.session_state:
        st.session_state.search_method = 'Search by Name and Industry'

    # Define callback function for radio button
    def on_search_method_change():
        st.session_state.search_method = st.session_state.search_method_radio

    # Search method selection    
    search_options = ["Search by Name and Industry", "Search by Company URL"]
    st.radio(
        "",
        options=search_options,
        key="search_method_radio",
        index=search_options.index(st.session_state.search_method),
        on_change=on_search_method_change
    )

    # Display input fields based on the selected search method
    if st.session_state.search_method == "Search by Name and Industry":
        company_name = st.text_input("Company Name", key="company_name_input")
        industry = st.text_input("Industry", key="industry_input")

        col1, col2 = st.columns([1, 1])
        with col1:
            research_button = st.button("Research Company", key="company_research_button")
        with col2:
            research_employees = st.checkbox('Research Employees', value=False)

        if research_button:
            if company_name and industry:
                with st.spinner('Researching company...'):
                    try:
                        company_result = run_async(insight_service.get_company_analysis(
                            company_name=company_name,
                            industry=industry,
                            scrape_employees=research_employees
                        ))
                        
                        st.session_state.company_insight_result = company_result
                        st.success("Company research completed!")
                        st.session_state.search_completed = True  # Set flag when search is successful

                        # Store company data in session state
                        st.session_state.company_data = company_result.company

                        # Display results
                        display_company_data(company_result.company)

                    except ApiError as e:
                        st.error(f"API Error: {e.error_message}")
                        st.session_state.search_completed = False
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.session_state.search_completed = False
            else:
                st.warning("Please provide both Company Name and Industry.")

    elif st.session_state.search_method == "Search by Company URL":
        company_url = st.text_input("Company URL", key="company_url_input")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            url_research_button = st.button("Research Company by URL")
        with col2:
            research_employees = st.checkbox('Research Employees', value=False)

        # Move the research logic outside of the columns
        if url_research_button:
            if company_url:
                with st.spinner('Researching company by URL...'):
                    try:
                        company_result = run_async(insight_service.get_company_analysis_by_url(
                            company_url=company_url,
                            scrape_employees=st.session_state.get('research_employees', False)
                        ))
                        
                        st.session_state.company_insight_result = company_result
                        st.success("Company research completed!")
                        st.session_state.search_completed = True  # Set flag when search is successful

                        # Store company data in session state
                        st.session_state.company_data = company_result.company

                        # Display results
                        display_company_data(company_result.company)

                    except ApiError as e:
                        st.error(f"API Error: {e.error_message}")
                        st.session_state.search_completed = False
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.session_state.search_completed = False
            else:
                st.warning("Please provide a Company URL.")

    # Save Company Search Button - Only show after successful search
    if st.session_state.get('search_completed', False):
        if st.button("💾 Save Company Search"):
            if st.session_state.company_data:  # Ensure company data exists
                save_company_search(user_email, st.session_state.company_data)
                st.success("Company search saved successfully!")
            else:
                st.warning("No company data to save.")


def display_company_data(company: Company):
    inject_css()
    st.markdown("<h2>🏢 Company Information</h2>", unsafe_allow_html=True)
    # Store company data in session state
    st.session_state.company_data = company

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