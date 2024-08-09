#!/usr/bin/env python
import sys
from insight_tracker.profile_crew import InsightTrackerCrew
from insight_tracker.company_crew import CompanyInsightTrackerCrew 
from insight_tracker.company_person_crew import CompanyPersonInsightTrackerCrew
import streamlit as st
import ast


st.title("Profile Insight Tracker")
name = st.text_input("Name")
company = st.text_input("Company")
if(st.button("Research")) :
    inputs = {
        'profile': name,
        'company': company
    }
    result = InsightTrackerCrew().crew().kickoff(inputs=inputs)
    st.markdown(result.tasks_output[1].raw)
    st.text_area(label='Draft Email to Reach' + name, value=result, height=300)

st.title("Company Insight Tracker")
company_name = st.text_input("Company Name")
industry = st.text_input("Industry")
if(st.button("Reserach Company")) :
    company_inputs = {
        'company': company_name,
        'industry':industry
    }
    result_company = CompanyInsightTrackerCrew().company_crew().kickoff(inputs=company_inputs)
    st.markdown(result_company.tasks_output[0].raw)
    st.markdown(result_company.tasks_output[1].raw)
    st.markdown(result_company.tasks_output[2].raw)
    st.markdown(type(result_company.tasks_output[2].raw))

    clean_data_string = result_company.tasks_output[2].raw.replace("```python", "").replace("```", "")
    dict_obj = ast.literal_eval(clean_data_string)
    st.markdown(type(dict_obj))



    if isinstance(dict_obj, list):
        category_names = [item['category'] for item in dict_obj]
        selected_category = st.selectbox("Select a category", category_names)

        
        selected_subpage = next(item['subpage'] for item in dict_obj if item['category'] == selected_category)

        input_two = {
            'category' : selected_subpage
        }
        result = CompanyPersonInsightTrackerCrew().company_person_crew().kickoff(inputs=input_two)
        st.markdown(result_company.tasks_output[0].raw)



# Create a dropdown for user to select a category

# Find the subpage URL corresponding to the selected category


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
