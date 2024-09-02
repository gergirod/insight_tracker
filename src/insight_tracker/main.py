#!/usr/bin/env python
import sys
from dotenv import load_dotenv

#load_dotenv()
from insight_tracker.profile_crew import InsightTrackerCrew
from insight_tracker.company_crew import CompanyInsightTrackerCrew 
from insight_tracker.company_person_crew import CompanyPersonInsightTrackerCrew
import streamlit as st
from streamlit_option_menu import option_menu
import asyncio


def convert_urls_to_dicts(urls, key="url"):
    return [{key: url} for url in urls]

async def runCrew(resultInput) :
    result =  await CompanyPersonInsightTrackerCrew().company_person_crew().kickoff_for_each_async(inputs=resultInput)

    for a in result:
        st.markdown(a.tasks_output[0].raw)
        st.markdown(a.token_usage)
    

with st.sidebar:
        selected = option_menu(
            menu_title="Insight Tracker",
            options=["Profile Insight", "Company Insight", "Logout"],
            default_index=0
        )

if(selected == "Profile Insight"):
            
    st.header("Profile Insight")
    name = st.text_input("Name")
    company = st.text_input("Company")
    if(st.button("Research")) :
        inputs = {
            'profile': name,
            'company': company
            }
        result = InsightTrackerCrew().crew().kickoff(inputs=inputs)
        st.markdown(result.tasks_output[1].raw)
        st.text_area(label='Draft Email to Reach ' + name, value=result, height=300)
        
elif(selected == "Company Insight"):
             
    st.header("Company Insight")
    # Initialize session state variables if they don't exist
    if 'company_name' not in st.session_state:
        st.session_state.company_name = ''
    if 'industry' not in st.session_state:
        st.session_state.industry = ''
    if 'result_company' not in st.session_state:
        st.session_state.result_company = None
    if 'dict_obj' not in st.session_state:
        st.session_state.dict_obj = None
    if 'category_names' not in st.session_state:
        st.session_state.category_names = []
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = ''
    if 'selected_subpage' not in st.session_state:
        st.session_state.selected_subpage = ''

    if 'selected_person' not in st.session_state:
        st.session_state.selected_person = ''

    if 'company_task_running' not in st.session_state:
        st.session_state.company_task_running = False  # To check if the task is running
    if 'company_task_completed' not in st.session_state:
        st.session_state.company_task_completed = False 

    if 'person_company_task_running' not in st.session_state:
        st.session_state.person_company_task_running = False  # To check if the task is running
    if 'person_company_task_completed' not in st.session_state:
        st.session_state.person_company_task_completed = False 

    # Input fields
    st.session_state.company_name = st.text_input("Company Name", st.session_state.company_name)
    st.session_state.industry = st.text_input("Industry", st.session_state.industry)

    # Button to research the company
    if st.button("Research Company") and not st.session_state.company_task_running:

        st.session_state.company_task_running = True
        st.session_state.company_task_completed = False
        company_inputs = {
            'company': st.session_state.company_name,
            'industry': st.session_state.industry
        }

        st.session_state.person_company_task_running = True
        st.session_state.person_company_task_completed = False

        with st.spinner('Scraping Company Information... Please wait...'):
            st.session_state.result_company = CompanyInsightTrackerCrew().company_crew().kickoff(inputs=company_inputs)
                    
        st.session_state.person_company_task_running = False
        st.session_state.person_company_task_completed = True
                   
        st.markdown('Company Insight')
        st.markdown(st.session_state.result_company.tasks_output[2].raw)
        st.markdown(st.session_state.result_company.token_usage)
        st.markdown('People')
        list = st.session_state.result_company.tasks_output[4].pydantic
        result = convert_urls_to_dicts(list.employee_list)
        with st.spinner("Scraping People Information ... Please wait ..."):
            asyncio.run(runCrew(result))


# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding necessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

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
