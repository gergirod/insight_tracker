import streamlit as st
from insight_tracker.company_person_crew import CompanyPersonInsightTrackerCrew
import pandas as pd

def convert_urls_to_dicts(urls, user=None, key="url"):
    return [
        {
            key: url,
            'user_name': user[1] if user is not None else "[Your Name]",
            'user_job_title': user[3] if user is not None else "[Company title]",
            'user_company': user[4] if user is not None else "[Company]",
            'user_email': user[2] if user is not None else "[Your Email]"
        }
        for url in urls
    ]

async def run_company_person_crew(url_list):
    """
    Run the CompanyPersonInsightTrackerCrew asynchronously and store results.
    """
    if not st.session_state.final_crew_result:
        st.session_state.final_crew_result = await CompanyPersonInsightTrackerCrew().company_person_crew().kickoff_for_each_async(inputs=url_list)
        for output in st.session_state.final_crew_result:
            st.session_state.people_list.append(output.tasks_output[0].pydantic)
        st.session_state.persons_data_frame = pd.DataFrame([person.dict() for person in st.session_state.people_list])
