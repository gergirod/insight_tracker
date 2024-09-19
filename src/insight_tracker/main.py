#!/usr/bin/env python
#!/usr/bin/env python
import sys
import asyncio
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from insight_tracker.auth import login, handle_callback, signup

# Import your custom modules
from insight_tracker.profile_crew import InsightTrackerCrew
from insight_tracker.company_crew import CompanyInsightTrackerCrew
from insight_tracker.company_person_crew import CompanyPersonInsightTrackerCrew
from insight_tracker.company_crew import Company
from insight_tracker.company_person_crew import Profile
from insight_tracker.profile_crew import ProfessionalProfile
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
        'persons_data_frame': None,
        'company_data_frame': None,
        'company_inputs': {},
        'person_inputs': {},
        'nav_bar_option_selected': 'Profile Insight',
        'profile_research_trigger': False,
        'company_research_trigger': False,
        'user': None,
        'name': None
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
        st.session_state.persons_data_frame = pd.DataFrame([person.dict() for person in st.session_state.people_list])

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

# Function to display profile data
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

# Function to display company data
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

def display_side_bar():
    # -------------------- Sidebar Navigation -------------------- #
    with st.sidebar:
        if 'user' in st.session_state:
            st.session_state.nav_bar_option_selected = option_menu(
                menu_title="Insight Tracker",
            options=["Profile Insight", "Company Insight", "Settings", "Logout"],
            default_index=0,
            key="navigation_menu"
        )

def inject_profesional_profile_css():
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

# Function to display professional profile data
def display_professional_profile(profile: ProfessionalProfile):
    inject_profesional_profile_css()

    if profile.full_name:
        st.markdown(f"<p class='section-header'>👤 Full Name:</p><p class='small-text'>{profile.full_name}</p>", unsafe_allow_html=True)
    if profile.current_job_title:
        st.markdown(f"<p class='section-header'>💼 Current Job Title:</p><p class='small-text'>{profile.current_job_title}</p>", unsafe_allow_html=True)
    if profile.profesional_background:
        st.markdown(f"<p class='section-header'>📝 Professional Background:</p><p class='small-text'>{profile.profesional_background}</p>", unsafe_allow_html=True)
    if profile.past_jobs:
        st.markdown(f"<p class='section-header'>📜 Past Jobs:</p><p class='small-text'>{profile.past_jobs}</p>", unsafe_allow_html=True)
    if profile.key_achievements:
        st.markdown(f"<p class='section-header'>🏆 Key Achievements:</p><p class='small-text'>{profile.key_achievements}</p>", unsafe_allow_html=True)
    if profile.contact:
        st.markdown(f"<p class='section-header'>📞 Contact Information:</p><p class='small-text'>{profile.contact}</p>", unsafe_allow_html=True)


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
        display_professional_profile(result.tasks_output[1].pydantic)
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
        display_company_data(st.session_state.result_company.tasks_output[2].pydantic)
        display_people_data()


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
        .save-button, .scrape-button {
            background-color: #4CAF50;
            color: white;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .scrape-button {
            background-color: #1f77b4;
            margin-left: 10px;
        }
        .save-button:hover, .scrape-button:hover {
            background-color: #45a049;
        }
        .scrape-button:hover {
            background-color: #005f8c;
        }
        </style>
    """, unsafe_allow_html=True)

# -------------------- Company Insight Section -------------------- #
def settings_section():
    st.header("Settings")

    inject_settings_css()  # Inject CSS for styling

    # Input fields for the user settings
    full_name = st.text_input("Full Name", placeholder="Enter your full name", value=st.session_state.user.get('name'))
    role_position = st.text_input("Role/Position", placeholder="Enter your role or position")
    company = st.text_input("Company", placeholder="Enter your company name")
    company_url = st.text_input("Company URL", placeholder="Enter the company URL for scraping")

    # Layout for the buttons
    col1, col2 = st.columns([1, 1])

    # Save button
    with col1:
        if st.button("Save", key="save_button"):
            # Simulate saving the data (this could be saving to a database or file)
            st.success(f"Settings saved! \nName: {full_name} \nRole: {role_position} \nCompany: {company}")
            # Store the settings in session state (this allows you to reuse the settings elsewhere in the app)
            st.session_state['full_name'] = full_name
            st.session_state['role_position'] = role_position
            st.session_state['company'] = company
            st.session_state['company_url'] = company_url

    # Scrape or Research button
    with col2:
        if st.button("Scrape/Research", key="scrape_button"):
            if company_url:
                st.info(f"Initiating scraping or research for {company_url}...")
                # Simulate scraping logic
                st.success(f"Scraping or researching data from {company_url} completed!")
            else:
                st.error("Please enter a valid URL before scraping.")

def auth_section():
    # Minimal CSS for clean and centered layout without scroll issues
    st.markdown("""
        <style>
        /* Center content vertically and horizontally */
        .full-height-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 0;
        }

        /* Title Styling */
        .main-title {
            font-size: 2.5rem;
            color: #333;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* Description Styling */
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 30px;
        }

        </style>
    """, unsafe_allow_html=True)

    # Full height container to ensure proper centering
    st.markdown('<div class="full-height-container">', unsafe_allow_html=True)
    
    # Start content structure inside the centered container
    st.markdown('<div>', unsafe_allow_html=True)
    
    # Display title and subtitle
    st.markdown('<h1 class="main-title">Welcome to Insight Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Please log in or sign up to continue</p>', unsafe_allow_html=True)
    
    # Display the login button
    login()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close the inner div
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close the full-height container

# Call the function to display the landing page


# Call the function to display the landing page



    

# -------------------- Main Application Flow -------------------- #
def main():
    if 'code' in st.query_params and st.session_state.user is None:
        handle_callback()
    # Check if the user is logged in
    if st.session_state.user is None:
        auth_section()
    else:

        display_side_bar()
        # Your existing main application logic goes here
        if st.session_state.nav_bar_option_selected == "Profile Insight":
            profile_insight_section()
        elif st.session_state.nav_bar_option_selected == "Company Insight":
            company_insight_section()
        elif st.session_state.nav_bar_option_selected == "Settings":
            settings_section()
        elif st.session_state.nav_bar_option_selected == "Logout":
            del st.session_state['user']
            st.rerun()
        else:
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
