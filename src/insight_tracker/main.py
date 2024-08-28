#!/usr/bin/env python
import sys
from dotenv import load_dotenv

#load_dotenv()
import agentops
#agentops.init()
from insight_tracker.profile_crew import InsightTrackerCrew
from insight_tracker.company_crew import CompanyInsightTrackerCrew 
from insight_tracker.company_person_crew import CompanyPersonInsightTrackerCrew
import streamlit as st
import ast
import re
from streamlit_option_menu import option_menu

def convert_urls_to_dicts(urls, key="url"):
    return [{key: url} for url in urls]

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

    # Input fields
    st.session_state.company_name = st.text_input("Company Name", st.session_state.company_name)
    st.session_state.industry = st.text_input("Industry", st.session_state.industry)

    # Button to research the company
    if st.button("Research Company"):
        company_inputs = {
            'company': st.session_state.company_name,
            'industry': st.session_state.industry
        }
        st.session_state.result_company = CompanyInsightTrackerCrew().company_crew().kickoff(inputs=company_inputs)
                    
                   
        # st.markdown('Website')
        # st.markdown(st.sessyion_state.result_company.tasks_output[1].raw)
        st.markdown('Company Insight')
        st.markdown(st.session_state.result_company.tasks_output[2].raw)
        st.markdown('People')
        list = st.session_state.result_company.tasks_output[4].pydantic
        st.markdown(list)
        result = convert_urls_to_dicts(list.employee_list)
        #st.markdown(type(result))
        #st.markdown(result)

        final_result = CompanyPersonInsightTrackerCrew().company_person_crew().kickoff_for_each(inputs=result)


        #st.markdown(final_result)

        for a in final_result:
            st.markdown(a.tasks_output[0].raw)

        # result = st.session_state.result_company.tasks_output[5].pydantic

        # for profile in result.profile_list:
        #      # Create columns for the layout
        #     col1, col2 = st.columns([4, 1])
    
        #     with col1:
        #         #st.image(profile.profile_image, width=100)
        #         st.write(f"**Name:** {profile.full_name}")
        #         st.write(f"**Role:** {profile.role}")
        #         st.write(f"**Background Experience:** {profile.background_experience}")
        #         st.write(f"**Contact Info: ** {profile.contact}")

        # #     with col2:
        # #         # Create a radio button to select one person
        # #         if st.radio("", [profile.full_name] if st.session_state.selected_person != profile.full_name else 0) == profile.full_name:
        # #             st.session_state.selected_person = profile

        # st.markdown('Outreach Emails')
        # st.markdown(st.session_state.result_company.tasks_output[6].raw)



    # Create a sidebar for navigation

    # matches = re.findall(r'\[.*?\]', st.session_state.result_company.tasks_output[3].raw)
    # result = ''.join(matches)
    # print(result)
    # st.markdown(result)
    # finalList = ast.literal_eval(result)

    # if 'selected_person' not in st.session_state:
    #     st.session_state.selected_person = None

    # st.title("Select a Person for Outreach")

    # for person in finalList:
    #     # Create columns for the layout
    #     col1, col2 = st.columns([4, 1])
    
    #     with col1:
    #         st.image(person["Profile Image Url"], width=100)
    #         st.write(f"**Name:** {person['Full Name']}")
    #         st.write(f"**Role:** {person['Role']}")
    #         st.write(f"**Background Experience:** {person['Background Experience']}")
    #         st.write(f"[Contact Info]({person['Contact']})")

    #     with col2:
    #         # Create a radio button to select one person
    #         if st.radio("", [person["Full Name"], None], index=1 if st.session_state.selected_person != person["Full Name"] else 0) == person["Full Name"]:
    #             st.session_state.selected_person = person["Full Name"]
    


    # Process the third task's output
#     st.session_state.clean_data_string = st.session_state.result_company.tasks_output[3].raw.replace("```python", "").replace("```", "")
#     st.session_state.dict_obj = ast.literal_eval(st.session_state.clean_data_string)

#     # If dict_obj is a list, extract category names
#     if isinstance(st.session_state.dict_obj, list):
#         st.session_state.category_names = [item['category'] for item in st.session_state.dict_obj]

# # Show category selection if the company has been researched
# if st.session_state.dict_obj:
#     st.session_state.selected_category = st.selectbox("Select a category", st.session_state.category_names)

#     # Find subpages for the selected category
#     st.session_state.selected_subpage = next(item['subpage'] for item in st.session_state.dict_obj if item['category'] == st.session_state.selected_category)

#     # Button to search for a person based on the selected subpage
#     if st.button('Search Person'):
#         input_two = {
#             'category': st.session_state.selected_subpage
#         }
#         result = CompanyPersonInsightTrackerCrew().company_person_crew().kickoff(inputs=input_two)
#         st.markdown( result.tasks_output[0].raw)
#         st.markdown( result.tasks_output[1].raw)
    

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
