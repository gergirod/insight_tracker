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

def inject_css():
    st.markdown("""
        <style>
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            background-color: #007bff;
            color: white !important;
            border: none;
            transition: all 0.2s ease;
            margin-top: 1rem;
        }
        
        .stButton > button:hover {
            background-color: #0056b3;
            color: white !important;
            border: none;
        }
        
        /* Save button specific styling */
        .stButton > button:has(div:contains("💾")) {
            background-color: #28a745;
            color: white !important;
            margin-top: 0.5rem;
        }
        
        .stButton > button:has(div:contains("💾")):hover {
            background-color: #218838;
            color: white !important;
        }

        /* Disabled button styling */
        .stButton > button:disabled {
            background-color: #6c757d !important;
            opacity: 0.65;
            cursor: not-allowed;
            color: white !important;
        }

        /* Input field styling */
        .stTextInput > div > div {
            border-radius: 4px;
        }

        /* Add spacing between input fields */
        .stTextInput {
            margin-bottom: 0.5rem;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 1rem;
            font-weight: 600;
        }

        /* Ensure button text stays white in all states */
        .stButton > button:active, 
        .stButton > button:focus,
        .stButton > button:visited {
            color: white !important;
        }

        /* Ensure button content (text and emoji) stays white */
        .stButton > button > div {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def profile_insight_section():
    inject_css()
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
                    st.session_state.search_completed = True
                
                st.success("Research completed!")
                
            except ApiError as e:
                st.error(f"API Error: {e.error_message}")
                st.session_state.search_completed = False
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error(f"Error details: {type(e).__name__}")
                st.session_state.search_completed = False
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

            # Optional Proposal URL field
            st.markdown("### Optional")
            proposal_url = st.text_input("Proposal URL", key="proposal_url_input", 
                                       help="Add a proposal URL to include in the outreach email")

            # Action buttons in horizontal layout
            col1, col2 = st.columns(2)
            with col1:
                generate_email = st.button("Generate Outreach Email")
                if generate_email:
                    st.markdown("🔄 Crafting personalized email...")  # Local loading message
                    user = getUserByEmail(user_email)
                    sender_info = {
                        "full_name": user[1] if user else "[Your Name]",
                        "company": user[4] if user else "[Company]",
                        "role": user[3] if user else "[Company title]"
                    }
                    profile_data = profile.__dict__
                    # Add proposal URL to the request if provided
                    if proposal_url:
                        profile_data['proposal_url'] = proposal_url
                        
                    email_result = run_async(
                        insight_service.generate_outreach_email(
                            profile_data=profile_data,
                            sender_info=sender_info
                        )
                    )
                    st.session_state.email_result = email_result
                    st.success("Email generated successfully!")

            with col2:
                st.button("Prepare for Meeting", disabled=True, key="prepare_meeting_button")

        # Email section
        if 'email_result' in st.session_state:
            st.subheader("✉️ Outreach Email")
            email_result = st.session_state.email_result
            email_content = email_result.email
            
            if email_result.subject:
                st.markdown(f"**Subject:** {email_result.subject}")
                
            st.text_area(
                "Draft Email",
                value=email_content,
                height=200,
                key="email_content"
            )

        if st.button("💾 Save Research", key="save_button"):
            save_profile_search(user_email, profile, person_company)
            st.success("Research saved successfully!")
            