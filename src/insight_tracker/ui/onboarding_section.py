import streamlit as st
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.db import save_user_company_info, create_user_if_not_exists
import os
import asyncio
from insight_tracker.ui.components.loading_dialog import show_loading_dialog

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def onboarding_section(user_email):
    # Initialize onboarding data
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {
            'full_name': st.session_state.user.get('name', ''),
            'email': user_email
        }

    # Header
    st.markdown("""
        <h1 style="color: #2C3E50; font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">👋 Welcome!</h1>
        <p style="color: #666; text-align: center; margin-bottom: 2rem;">Let's personalize your experience</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 6])
    
    with col1:
        with st.container():
            st.markdown("##### Why we need this information")
            st.caption("""
                This information helps us provide you with:
                • AI-powered profile insights
                • Smart outreach suggestions
                • Company analysis
                • Meeting preparation strategies
                • Fit evaluation recommendations
                
                All tailored to your professional context for more meaningful connections.
            """)

    with col2:
        # User info display
        st.markdown("""
            <div style="background: white; border: 1px solid #eee; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
                <div style="margin-bottom: 1rem;">
                    <label style="color: #666; font-size: 0.9rem; display: block; margin-bottom: 0.3rem;">
                        Full Name
                    </label>
                    <div style="color: #1E88E5; font-weight: 500; font-size: 1.1rem;">
                        {}
                    </div>
                </div>
                <div>
                    <label style="color: #666; font-size: 0.9rem; display: block; margin-bottom: 0.3rem;">
                        Email
                    </label>
                    <div style="color: #1E88E5; font-weight: 500; font-size: 1.1rem;">
                        {}
                    </div>
                </div>
            </div>
        """.format(
            st.session_state.onboarding_data['full_name'],
            user_email
        ), unsafe_allow_html=True)

        # Form inputs
        role = st.text_input(
            "Role/Position",
            value=st.session_state.onboarding_data.get('role', ''),
            placeholder="e.g., Sales Director, Marketing Manager"
        )

        company_input_method = st.radio(
            "How would you like to provide company information?",
            options=["Company Name & Industry", "Company URL"],
            horizontal=True
        )

        if company_input_method == "Company Name & Industry":
            company = st.text_input(
                "Company Name",
                value=st.session_state.onboarding_data.get('company', ''),
                placeholder="e.g., Acme Corporation"
            )
            industry = st.text_input(
                "Industry",
                value=st.session_state.onboarding_data.get('company_industry', ''),
                placeholder="e.g., Technology, Healthcare"
            )
            continue_disabled = not (role and company and industry)
        else:
            company_url = st.text_input(
                "Company Website",
                value=st.session_state.onboarding_data.get('company_url', ''),
                placeholder="e.g., https://company.com"
            )
            continue_disabled = not (role and company_url)

        # Complete Setup button
        if st.button(
            "Complete Setup →",
            disabled=continue_disabled,
            type="primary",
            use_container_width=True
        ):
            try:
                # Show loading dialog
                loading_container = show_loading_dialog(
                    title="Setting up your personalized workspace",
                    description="We're analyzing your professional context, gathering company insights, and preparing AI-powered recommendations to help you create meaningful connections.",
                    loading_message="Just a moment while we set everything up..."
                )

                # Save user data first
                create_user_if_not_exists(
                    full_name=st.session_state.onboarding_data['full_name'],
                    email=user_email,
                    role=role,
                    company=company if company_input_method == "Company Name & Industry" else ""
                )

                # Initialize API client
                api_client = InsightApiClient(
                    base_url=os.getenv('API_BASE_URL'),
                    api_key=os.getenv('API_KEY'),
                    openai_api_key=os.getenv('OPENAI_API_KEY'),
                    verify_ssl=False
                )
                insight_service = InsightService(api_client)

                # Get company data based on input method
                if company_input_method == "Company Name & Industry":
                    company_insight = run_async(
                        insight_service.get_company_analysis(
                            company_name=company,
                            industry=industry
                        )
                    )
                else:
                    company_insight = run_async(
                        insight_service.get_company_analysis_by_url(
                            company_url=company_url
                        )
                    )

                if company_insight and company_insight.company:
                    loading_container.empty()  # Clear the loading dialog
                    save_user_company_info(user_email, company_insight.company)
                    
                    # Update session state
                    st.session_state.onboarding_complete = True
                    st.session_state.nav_bar_option_selected = "Profile Insight"
                    st.session_state.setup_complete = True
                    
                    # Show success message
                    st.success("✅ Your workspace is ready!")
                    st.rerun()
                else:
                    loading_container.empty()  # Clear the loading dialog
                    st.error("❌ We couldn't set up your workspace. Please try again.")
            except Exception as e:
                loading_container.empty()  # Clear the loading dialog
                st.error(f"❌ Something went wrong during setup: {str(e)}") 