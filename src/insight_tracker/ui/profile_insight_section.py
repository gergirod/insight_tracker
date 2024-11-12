import streamlit as st
import os
import asyncio
import warnings
import urllib3
from insight_tracker.db import getUserByEmail, save_profile_search, get_recent_profile_searches
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.exceptions.api_exceptions import ApiError

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_async(coroutine):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def profile_insight_section():
    st.header("Profile Insight")
    
    user_email = st.session_state.user.get('email')
    
    # Initialize API service with SSL verification disabled
    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )
    insight_service = InsightService(api_client)

    # Input fields with memory
    person_name = st.text_input("Name", key="person_name_input")
    person_company = st.text_input("Company", key="person_company_input")

    if st.button("Research", key="profile_research_button"):
        if person_name and person_company:
            try:
                # Profile Analysis
                with st.spinner('Analyzing profile...'):
                    profile_result = run_async(
                        insight_service.get_profile_analysis(
                            full_name=person_name,
                            company_name=person_company
                        )
                    )
                    st.session_state.profile_result = profile_result

                if profile_result:
                    with st.spinner('Generating email...'):
                        print("User email:")
                        print(user_email)
                        user = getUserByEmail(user_email)
                        print("User:")
                        print(user)
                        print("--------------------------------")
                        
                        sender_info = {
                            "full_name": user[1] if user else "[Your Name]",
                            "company": user[4] if user else "[Company]",
                            "role": user[3] if user else "[Company title]"
                        }
                        
                        # Convert profile_result.profile to a dictionary
                        profile_data = profile_result.profile.__dict__  # Assuming profile is a standard class
                       
                        email_result = run_async(
                            insight_service.generate_outreach_email(
                                profile_data=profile_data,  # Updated to use the dictionary
                                sender_info=sender_info
                            )
                        )
                        st.session_state.email_result = email_result
                
                st.success("Research completed!")
                
            except ApiError as e:
                st.error(f"API Error: {e.error_message}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error(f"Error details: {type(e).__name__}")  # Added for debugging
        else:
            st.warning("Please provide both Name and Company.")

    # Display results
    if 'profile_result' in st.session_state:
        with st.container():
            st.subheader("👤 Profile Information")
            response = st.session_state.profile_result
            profile = response.profile
                        
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"**Name:** {profile.full_name}")
                st.markdown(f"**Title:** {profile.current_job_title}")
                st.markdown(f"**Contact:** {profile.contact}")
            
            with cols[1]:
                if profile.linkedin_url:
                    st.markdown(f"**LinkedIn:** [{profile.linkedin_url}]({profile.linkedin_url})")
                st.markdown(f"**Company:** {person_company}")

            with st.expander("📚 Professional Background", expanded=True):
                st.markdown(profile.professional_background)
            
            with st.expander("💼 Past Experience"):
                st.markdown(profile.past_jobs)
            
            with st.expander("🏆 Key Achievements"):
                st.markdown(profile.key_achievements)

        # Email section
        if 'email_result' in st.session_state:
            st.subheader("✉️ Outreach Email")
            email_result = st.session_state.email_result
            # Fix: Access the email content directly
            email_content = email_result.email  # Changed from email_result.profile.get()
            
            if email_result.subject:
                st.markdown(f"**Subject:** {email_result.subject}")
                
            st.text_area(
                "Draft Email",
                value=email_content,
                height=200,
                key="email_content"
            )

        # Save results
        if st.button("💾 Save Research", key="save_button"):
            save_profile_search(user_email, profile, person_company)
            st.success("Research saved successfully!")

        # Clear results
        if st.button("🗑️ Clear Results", key="clear_button"):
            for key in ['profile_result', 'email_result']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()