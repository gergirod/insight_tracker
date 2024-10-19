import streamlit as st
from insight_tracker.db import getUserByEmail, save_profile_search, get_recent_profile_searches
from insight_tracker.profile_crew import InsightTrackerCrew, ProfessionalProfile

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

    # ... (keep existing CSS)

def clear_previous_search_data():
    """Clear the previous search data from session state"""
    st.session_state.company_insight_tracker_result = None
    if 'draft_email_area' in st.session_state:
        del st.session_state.draft_email_area

def profile_insight_section():
    st.header("Profile Insight")
    
    user_email = st.session_state.user.get('email')
    
    st.session_state.person_name = st.text_input("Name", value=st.session_state.person_name, key="person_name_input")
    st.session_state.person_company = st.text_input("Company", value=st.session_state.person_company, key="person_company_input")

    if st.button("Research", key="profile_research_button"):
        user = getUserByEmail(user_email)
        if st.session_state.person_name and st.session_state.person_company:
            st.session_state.person_inputs = {
                'profile': st.session_state.person_name,
                'company': st.session_state.person_company,
                'user_name': user[1] if user is not None else "[Your Name]",
                'user_job_title' : user[3] if user is not None else "[Company title]",
                'user_company' : user[4] if user is not None else "[Company]",
                'user_email' : user[2] if user is not None else "[Your Email]"
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
        profile = result.tasks_output[1].pydantic
        display_professional_profile(profile)
        st.text_area(
            label=f'Draft Email to Reach {st.session_state.person_name}',
            value=result.tasks_output[2].raw if len(result.tasks_output) > 2 else "",
            height=300,
            key="draft_email_area"
        )
        
        # Add save button
        if st.button("Save Search", key="save_profile_search"):
            save_profile_search(user_email, profile)
            st.success("Search saved successfully!")

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