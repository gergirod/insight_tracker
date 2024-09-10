#!/usr/bin/env python
#!/usr/bin/env python
import sys
import asyncio
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

# Import your custom modules
from insight_tracker.profile_crew import InsightTrackerCrew
from insight_tracker.company_crew import CompanyInsightTrackerCrew
from insight_tracker.company_person_crew import CompanyPersonInsightTrackerCrew

# -------------------- Session State Initialization -------------------- #
def initialize_session_state():
    default_values = {
        'person_name': '',
        'person_company': '',
        'company_name': '',
        'industry': '',
        'people_list': [],
        'result_company': None,
        'company_task_running': False,
        'company_task_completed': False,
        'pydantic_url_list': [],
        'url_list_dict': [],
        'current_view': 'List View',
        'final_crew_result': [],
        'company_insight_tracker_result': None,
        'data_frame': None,
        'company_inputs': {},
        'person_inputs': {},
        'nav_bar_option_selected': 'Profile Insight',
        'profile_research_trigger': False,
        'company_research_trigger': False,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# -------------------- Utility Functions -------------------- #
def convert_urls_to_dicts(urls, key="url"):
    return [{key: url} for url in urls]

async def run_company_person_crew(url_list):
    """
    Run the CompanyPersonInsightTrackerCrew asynchronously and store results.
    """
    if not st.session_state.final_crew_result:
        st.session_state.final_crew_result = await CompanyPersonInsightTrackerCrew().company_person_crew().kickoff_for_each_async(inputs=url_list)
        for output in st.session_state.final_crew_result:
            st.session_state.people_list.append(output.tasks_output[0].pydantic)
        # Convert people_list to DataFrame
        st.session_state.data_frame = pd.DataFrame([person.dict() for person in st.session_state.people_list])

def display_people_data():
    """
    Display people data in either List View or Table View based on user selection.
    """

    if(st.session_state.people_list is not None and len(st.session_state.people_list) > 0): 
        st.subheader(f"{st.session_state.current_view}")
        if st.session_state.current_view == 'List View':
            for profile in st.session_state.people_list:
                st.markdown(f"**Name:** {profile.full_name}")
                #st.image(profile.profile_image, width=100)
                st.markdown(f"**Role:** {profile.role}")
                st.markdown(f"**Contact:** {profile.contact}")
                st.markdown(f"**Background Experience:** {profile.background_experience}")
                st.text_area(label=f'Draft Email to Reach {profile.full_name}',value=profile.outreach_email, height=300)
                st.markdown("---")
        elif st.session_state.current_view == 'Table View':
            if st.session_state.data_frame is not None:
                st.dataframe(st.session_state.data_frame)
            else:
                st.warning("No data available to display.")

# -------------------- Sidebar Navigation -------------------- #
with st.sidebar:
    st.session_state.nav_bar_option_selected = option_menu(
        menu_title="Insight Tracker",
        options=["Profile Insight", "Company Insight"],
        default_index=0,
        key="navigation_menu"
    )

# -------------------- Profile Insight Section -------------------- #
def profile_insight_section():
    st.header("Profile Insight")
    st.session_state.person_name = st.text_input("Name", value=st.session_state.person_name, key="person_name_input")
    st.session_state.person_company = st.text_input("Company", value=st.session_state.person_company, key="person_company_input")

    if st.button("Research", key="profile_research_button"):
        if st.session_state.person_name and st.session_state.person_company:
            st.session_state.person_inputs = {
                'profile': st.session_state.person_name,
                'company': st.session_state.person_company
            }
            with st.spinner('Researching profile...'):
                try:
                    result = InsightTrackerCrew().crew().kickoff(inputs=st.session_state.person_inputs)
                    st.session_state.company_insight_tracker_result = result
                    st.success("Profile research completed!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please provide both Name and Company.")

    # Display results if available
    if st.session_state.company_insight_tracker_result:
        result = st.session_state.company_insight_tracker_result
        st.markdown("### Research Result")
        st.markdown(result.tasks_output[1].raw)
        st.text_area(
            label=f'Draft Email to Reach {st.session_state.person_name}',
            value=result.tasks_output[2].raw if len(result.tasks_output) > 2 else "",
            height=300,
            key="draft_email_area"
        )

# -------------------- Company Insight Section -------------------- #
def company_insight_section():
    st.header("Company Insight")
    st.session_state.company_name = st.text_input("Company Name", value=st.session_state.company_name, key="company_name_input")
    st.session_state.industry = st.text_input("Industry", value=st.session_state.industry, key="industry_input")

    if st.button("Research Company", key="company_research_button"):
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
            except Exception as e:
                st.error(f"An error occurred during company research: {e}")
                st.session_state.company_task_completed = False

    # Fetch and display people data if company research is completed
    if st.session_state.company_task_completed and not st.session_state.people_list:
        try:
            st.session_state.pydantic_url_list = st.session_state.result_company.tasks_output[4].pydantic
            if(st.session_state.pydantic_url_list.employee_list is not None and len(st.session_state.pydantic_url_list.employee_list) > 0) :
                st.session_state.url_list_dict = convert_urls_to_dicts(st.session_state.pydantic_url_list.employee_list)
                with st.spinner("Scraping People Information... Please wait..."):
                    asyncio.run(run_company_person_crew(st.session_state.url_list_dict))
                st.success("People information scraped successfully!")
        except Exception as e:
            st.error(f"An error occurred while fetching people information: {e}")

    # Display company and people information
    if st.session_state.company_task_completed:
        st.markdown("### Company Insight")
        st.markdown(st.session_state.result_company.tasks_output[2].raw)

        # View Selection
        st.markdown("### People Information")
        display_people_data()

# -------------------- Main Application Flow -------------------- #
def main():
    if st.session_state.nav_bar_option_selected == "Profile Insight":
        profile_insight_section()
    elif st.session_state.nav_bar_option_selected == "Company Insight":
        company_insight_section()
    else:
        st.title("Welcome to Insight Tracker")
        st.write("Please select an option from the sidebar.")

if __name__ == "__main__":
    main()


def run():
    """
    Run the crew.
    """
    inputs = {
        'profile': '',
        'company': ''
    }
    InsightTrackerCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'profile': '',
        'company': ''
    }
    try:
        InsightTrackerCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        InsightTrackerCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
