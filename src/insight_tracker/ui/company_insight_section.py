import streamlit as st
from insight_tracker.company_crew import CompanyInsightTrackerCrew, Company
from insight_tracker.company_person_crew import Profile
from insight_tracker.db import getUserByEmail
from insight_tracker.utils.util import convert_urls_to_dicts
from insight_tracker.utils.util import run_company_person_crew
import asyncio
import pandas as pd



def company_insight_section():
    st.header("Company Insight")
    st.session_state.company_name = st.text_input("Company Name", value=st.session_state.company_name, key="company_name_input")
    st.session_state.industry = st.text_input("Industry", value=st.session_state.industry, key="industry_input")

    col1, col2 = st.columns([1, 1])
    with col1:
        research_button = st.button("Research Company", key="company_research_button")
    with col2:
        st.session_state.research_employees = st.checkbox('Research Employees', value=st.session_state.research_employees)

    if research_button:
        if st.session_state.company_name and st.session_state.industry:
            st.session_state.company_inputs = {
                'company': st.session_state.company_name,
                'industry': st.session_state.industry
            }
            st.session_state.company_research_trigger = True
        else:
            st.warning("Please provide both Company Name and Industry.")

    # Run company research if triggered
    if st.session_state.company_research_trigger and not st.session_state.company_task_completed:
        with st.spinner('Scraping Company Information... Please wait...'):
            try:
                st.session_state.result_company = CompanyInsightTrackerCrew().company_crew().kickoff(inputs=st.session_state.company_inputs)
                st.success("Company information scraped successfully!")
                st.session_state.company_task_completed = True

                # If research_employees is checked, immediately fetch employee data
                if st.session_state.research_employees:
                    st.session_state.pydantic_url_list = st.session_state.result_company.tasks_output[4].pydantic
                    if st.session_state.pydantic_url_list.employee_list is not None and len(st.session_state.pydantic_url_list.employee_list) > 0:
                        user_email = st.session_state.user.get('email')
                        user = getUserByEmail(user_email)
                        st.session_state.url_list_dict = convert_urls_to_dicts(st.session_state.pydantic_url_list.employee_list, user=user)
                        with st.spinner("Scraping People Information... Please wait..."):
                            asyncio.run(run_company_person_crew(st.session_state.url_list_dict))
                        st.success("People information scraped successfully!")

            except Exception as e:
                st.error(f"An error occurred during research: {e}")
                st.session_state.company_task_completed = False

    # Display company and people information
    if st.session_state.company_task_completed:
        st.markdown("### Company Insight")
        display_company_data(st.session_state.result_company.tasks_output[2].pydantic)
        if st.session_state.research_employees:
            display_people_data()

    # Reset the research trigger
    st.session_state.company_research_trigger = False


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

def display_company_data(company: Company):
    inject_css()
    st.markdown("<h2>🏢 Company Information</h2>", unsafe_allow_html=True)
    st.session_state.company_data_frame = pd.DataFrame([company.dict()])

    if st.session_state.company_data_frame is not None:
        st.dataframe(st.session_state.company_data_frame)

    if company.company_name:
        st.markdown(f"<p class='section-header'>🏷️ Company Name:</p><p class='small-text'>{company.company_name}</p>", unsafe_allow_html=True)
    if company.company_website:
        st.markdown(f"<p class='section-header'>🌐 Website:</p><p class='small-text'><a href='{company.company_website}' target='_blank'>{company.company_website}</a></p>", unsafe_allow_html=True)
    if company.company_summary:
        st.markdown(f"<p class='section-header'>📝 Summary:</p><p class='small-text'>{company.company_summary}</p>", unsafe_allow_html=True)
    if company.company_industry:
        st.markdown(f"<p class='section-header'>🏭 Industry:</p><p class='small-text'>{company.company_industry}</p>", unsafe_allow_html=True)
    if company.company_services:
        st.markdown(f"<p class='section-header'>🛠️ Services:</p><p class='small-text'>{company.company_services}</p>", unsafe_allow_html=True)
    if company.company_industries:
        st.markdown(f"<p class='section-header'>🏢 Industries:</p><p class='small-text'>{company.company_industries}</p>", unsafe_allow_html=True)
    if company.company_awards_recognitions:
        st.markdown(f"<p class='section-header'>🏆 Awards and Recognitions:</p><p class='small-text'>{company.company_awards_recognitions}</p>", unsafe_allow_html=True)
    if company.company_clients_partners:
        st.markdown(f"<p class='section-header'>🤝 Clients and Partners:</p><p class='small-text'>{company.company_clients_partners}</p>", unsafe_allow_html=True)

def display_people_data():
    """
    Display people data in either List View or Table View based on user selection.
    """

    view_option = st.radio(
        "Select View",
        options=["List View", "Table View"],
        index=0 if st.session_state.current_view == 'List View' else 1,
        key="view_selection_radio"
    )
    st.session_state.current_view = view_option

    if(st.session_state.people_list is not None and len(st.session_state.people_list) > 0): 
        st.markdown("### People Information")
        st.subheader(f"{st.session_state.current_view}")
        if st.session_state.current_view == 'List View':
            for profile in st.session_state.people_list:
                display_profile_data(profile)
        elif st.session_state.current_view == 'Table View':
            if st.session_state.persons_data_frame is not None:
                st.dataframe(st.session_state.persons_data_frame)
            else:
                st.warning("No data available to display.")

def inject_profile_css():
    st.markdown("""
        <style>
        .small-text {
            font-size: 16px;
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
        .link {
            color: #1f77b4;
            text-decoration: none;
        }
        .container {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            background-color: #fafafa;
        }
        </style>
    """, unsafe_allow_html=True)

def display_profile_data(profile: Profile):
    inject_profile_css()
    # Display the profile image, if available
    if profile.full_name:
        st.markdown(f"<p class='section-header'>👤 Full Name:</p><p class='small-text'>{profile.full_name}</p>", unsafe_allow_html=True)
    if profile.role:
        st.markdown(f"<p class='section-header'>💼 Role:</p><p class='small-text'>{profile.role}</p>", unsafe_allow_html=True)
    if profile.contact:
        st.markdown(f"<p class='section-header'>📞 Contact:</p><p class='small-text'>{profile.contact}</p>", unsafe_allow_html=True)
    if profile.background_experience:
        st.markdown(f"<p class='section-header'>📝 Background Experience:</p><p class='small-text'>{profile.background_experience}</p>", unsafe_allow_html=True)
    if profile.outreach_email:
        st.markdown(f"<p class='section-header'>📧 Outreach Email:</p><p class='small-text'>{profile.outreach_email}</p>", unsafe_allow_html=True)
