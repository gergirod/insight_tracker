import streamlit as st
import os
import asyncio
import urllib3
from insight_tracker.db import getUserByEmail, save_profile_search, get_user_company_info, decrease_user_usage_limit
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.exceptions.api_exceptions import ApiError
import re


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
                    st.session_state.fit_evaluated = False  # Reset fit evaluation flag
                
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

    # Display results only if research is completed
    if st.session_state.get('search_completed', False):
        if 'profile_result' in st.session_state:
            with st.container():
                st.subheader("👤 Profile Information")
                response = st.session_state.profile_result
                profile = response.profile
                            
                cols = st.columns(2)
                with cols[0]:
                    st.markdown(f"**👨‍💼 Name:** {profile.full_name}")
                    st.markdown(f"**🏢 Title:** {profile.current_job_title or 'N/A'}")
                    st.markdown(f"**🏢 Company:** {profile.current_company or 'N/A'}")
                    st.markdown(f"**🔗 Company URL:** {profile.current_company_url or 'N/A'}")
                    
                with cols[1]:
                    st.markdown(f"**📞 Contact:** {profile.contact or 'N/A'}")
                    st.markdown(f"**🔗 LinkedIn:** {profile.linkedin_url or 'N/A'}")

            with st.expander("📚 Professional Background", expanded=True):
                st.markdown(profile.professional_background)
            
            with st.expander("💼 Past Experience"):
                st.markdown(profile.past_jobs)
            
            with st.expander("🏆 Key Achievements"):
                st.markdown(profile.key_achievements)

            if st.button("💾 Save Research", key="save_button"):
                save_profile_search(user_email, profile)
                st.success("Research saved successfully!")

            # Action buttons in horizontal layout
            col1, col2, col3 = st.columns(3)
            user_company = get_user_company_info(user_email)
            user = getUserByEmail(user_email)

            with col1:
                user = getUserByEmail(user_email)
                user_company = get_user_company_info(user_email)
                
                generate_email = st.button("Generate Email", type="primary")
                if generate_email:

                    user_info = getUserByEmail(user_email)

                    if user_info and user_info[5] <= 0:  # Assuming free_usage_limit is at index 5
                        st.error("""
                            ⚠️ Usage Limit Reached
                            
                            You have reached your free usage limit for evaluations. 
                            Please contact support for more information about upgrading your account.
                        """)
                        return

                    decrease_user_usage_limit(user_email)
                    # Get latest user and company data
                    user = getUserByEmail(user_email)
                    user_company = get_user_company_info(user_email)
                    
                    # Check if we have all required information
                    missing_user_info = not user or not all([user[1]])  # name, role, company
                    missing_company_info = not user_company
                    
                    if missing_user_info or missing_company_info:
                        warning_message = []
                        if missing_user_info:
                            warning_message.append("• Complete your personal information (name, role, company)")
                        if missing_company_info:
                            warning_message.append("• Add your company information")
                        
                        st.warning(f"""
                            ⚠️ Additional information required
                            
                            To generate a personalized outreach email, please first:
                            {chr(10).join(warning_message)}
                            
                            This helps us create more effective and contextual communications.
                        """)
                        
                        if st.button("Complete Profile Settings →", type="primary"):
                            st.session_state.nav_bar_option_selected = "Settings"
                            st.rerun()
                    else:
                        try:
                            with st.spinner('Generating outreach email...'):
                                sender_info = {
                                    "full_name": user[1],
                                    "company": user[4],
                                    "role": user[3]
                                }
                                profile_data = profile.__dict__
                                
                                email_content = run_async(
                                    insight_service.generate_outreach_email(
                                        profile=profile_data,
                                        company=user_company.__dict__,
                                        sender_info=sender_info
                                    )
                                )
                                st.session_state.email_content = email_content
                                st.success("Email generated successfully!")
                        except Exception as e:
                            st.error(f"Failed to generate email: {str(e)}")

            with col2:
                
                prepare_meeting = st.button("Prepare for Meeting", type="primary")
                if prepare_meeting:

                    user_info = getUserByEmail(user_email)

                    if user_info and user_info[5] <= 0:  # Assuming free_usage_limit is at index 5
                        st.error("""
                            ⚠️ Usage Limit Reached
                            
                            You have reached your free usage limit for evaluations. 
                            Please contact support for more information about upgrading your account.
                        """)
                        return

                    decrease_user_usage_limit(user_email)
                    # Get latest user and company data
                    user_company = get_user_company_info(user_email)
                    # Check if we have all required information
                    missing_company_info = not user_company
                    
                    if missing_company_info:
                        warning_message = []
                        if missing_user_info:
                            warning_message.append("• Complete your personal information (name, role, company)")
                        if missing_company_info:
                            warning_message.append("• Add your company information")
                        
                        st.warning(f"""
                            ⚠️ Context Required for Meeting Preparation
                            
                            To create a personalized meeting strategy, please first:
                            {chr(10).join(warning_message)}
                            
                            This helps us provide more targeted talking points and strategic recommendations.
                        """)
                        
                        if st.button("Complete Profile Settings →", type="primary"):
                            st.session_state.nav_bar_option_selected = "Settings"
                            st.rerun()
                    else:
                        try:
                            with st.spinner('Preparing meeting strategy...'):
                                meeting_result = run_async(
                                    insight_service.prepare_meeting(
                                        profile=profile.__dict__,
                                        company=user_company.__dict__
                                    )
                                )
                                st.session_state.meeting_result = meeting_result
                                st.success("Meeting preparation completed!")
                        except Exception as e:
                            st.error(f"Failed to prepare meeting: {str(e)}")

            with col3:
                
                evaluate_fit = st.button("Evaluate Fit", type="primary")
                if evaluate_fit:

                    user_info = getUserByEmail(user_email)

                    if user_info and user_info[5] <= 0:  # Assuming free_usage_limit is at index 5
                        st.error("""
                            ⚠️ Usage Limit Reached
                            
                            You have reached your free usage limit for evaluations. 
                            Please contact support for more information about upgrading your account.
                        """)
                        return

                    decrease_user_usage_limit(user_email)
                    # Get latest company data
                    user_company = get_user_company_info(user_email)
                    
                    if not user_company:
                        st.warning("""
                            ⚠️ Company information required
                            
                            To evaluate profile fit, we need your company context. Please complete your company information in the Settings section first.
                            
                            This helps us provide more accurate and meaningful insights.
                        """)
                        
                        if st.button("Complete Company Settings →", type="primary"):
                            st.session_state.nav_bar_option_selected = "Settings"
                            st.rerun()
                    else:
                        try:
                            with st.spinner('Evaluating fit...'):
                                fit_result = run_async(
                                    insight_service.evaluate_profile_fit(
                                        profile=profile.__dict__,
                                        company=user_company.__dict__
                                    )
                                )
                                st.session_state.fit_evaluation_result = fit_result
                                st.success("Fit evaluation completed!")
                        except Exception as e:
                            st.error(f"Failed to evaluate fit: {str(e)}")

            # Display sections based on results
            
            # Email section
            if 'email_content' in st.session_state:
                with st.expander("✉️ Outreach Email", expanded=False):
                    clean_email = re.sub(r'<[^>]+>', '', st.session_state.email_content)

                    st.markdown(f"""
                            <div style="font-family: monospace; white-space: pre-wrap; padding: 1rem; font-size: 0.9rem; line-height: 1.5;">
                                {clean_email}
                            </div>
                    """, unsafe_allow_html=False)
                    

            # Meeting Preparation section
            if 'meeting_result' in st.session_state:
                with st.expander("📅 Meeting Preparation", expanded=False):
                    print(st.session_state.meeting_result)
                    print(type(st.session_state.meeting_result))
                    meeting_prep = st.session_state.meeting_result
                    
                    # Meeting Objectives
                    st.markdown('<div class="meeting-header">🎯 Meeting Objectives</div>', unsafe_allow_html=True)
                    for objective in meeting_prep.meeting_objectives:
                        st.markdown(f'<div class="meeting-item">• {objective}</div>', unsafe_allow_html=True)
                    
                    # Key Talking Points
                    st.markdown('<div class="meeting-header">💡 Key Talking Points</div>', unsafe_allow_html=True)
                    for point in meeting_prep.key_talking_points:
                        st.markdown(f'<div class="meeting-item">• {point}</div>', unsafe_allow_html=True)
                    
                    # Prepared Questions
                    st.markdown('<div class="meeting-header">❓ Prepared Questions</div>', unsafe_allow_html=True)
                    for question in meeting_prep.prepared_questions:
                        st.markdown(f'<div class="meeting-item">• {question}</div>', unsafe_allow_html=True)
                    
                    # Risk Factors
                    st.markdown('<div class="meeting-header">⚠️ Risk Factors</div>', unsafe_allow_html=True)
                    for risk in meeting_prep.risk_factors:
                        st.markdown(f'<div class="meeting-item risk-item">• {risk}</div>', unsafe_allow_html=True)
                    
                    # Success Metrics
                    st.markdown('<div class="meeting-header">📊 Success Metrics</div>', unsafe_allow_html=True)
                    for metric in meeting_prep.success_metrics:
                        st.markdown(f'<div class="meeting-item success-item">• {metric}</div>', unsafe_allow_html=True)
                    
                    # Next Steps
                    st.markdown('<div class="meeting-header">➡️ Next Steps</div>', unsafe_allow_html=True)
                    for step in meeting_prep.next_steps:
                        st.markdown(f'<div class="meeting-item next-step-item">• {step}</div>', unsafe_allow_html=True)
                    
                    # Follow-up Items
                    st.markdown('<div class="meeting-header">📝 Follow-up Items</div>', unsafe_allow_html=True)
                    for item in meeting_prep.follow_up_items:
                        st.markdown(f'<div class="meeting-item">• {item}</div>', unsafe_allow_html=True)

            # Fit Evaluation Results
            if 'fit_evaluation_result' in st.session_state:
                with st.expander("🔍 Fit Evaluation Results", expanded=False):
                    fit_result = st.session_state.fit_evaluation_result.evaluation

                    # Fit Score and Summary
                    st.markdown('<div class="meeting-header">📊 Overall Fit Assessment</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="meeting-item"><strong>Fit Score:</strong> {fit_result.fit_score if fit_result.fit_score is not None else "N/A"}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="meeting-item"><strong>Summary:</strong> {fit_result.fit_summary if fit_result.fit_summary is not None else "N/A"}</div>', unsafe_allow_html=True)

                    # Key Insights
                    st.markdown('<div class="meeting-header">💡 Key Insights</div>', unsafe_allow_html=True)
                    for insight in fit_result.key_insights:
                        st.markdown(f'<div class="meeting-item">• {insight}</div>', unsafe_allow_html=True)

                    # Expertise Matches
                    if fit_result.expertise_matches:
                        st.markdown('<div class="meeting-header">🎯 Expertise Matches</div>', unsafe_allow_html=True)
                        for match in fit_result.expertise_matches:
                            st.markdown(f"""
                                <div class="agenda-item">
                                    <div class="agenda-title">{match.area if match.area is not None else 'N/A'}</div>
                                    <div class="meeting-item">• Relevance Score: {match.relevance_score if match.relevance_score is not None else 'N/A'}</div>
                                    <div class="meeting-item">• {match.description if match.description is not None else 'N/A'}</div>
                                    <div class="meeting-item">• Evidence: {', '.join(match.evidence) if match.evidence else 'N/A'}</div>
                                </div>
                            """, unsafe_allow_html=True)

                    # Decision Maker Analysis
                    st.markdown('<div class="meeting-header">👔 Decision Maker Analysis</div>', unsafe_allow_html=True)
                    decision_maker_analysis = fit_result.decision_maker_analysis
                    if decision_maker_analysis:
                        st.markdown(f'<div class="meeting-item"><strong>Influence Level:</strong> {decision_maker_analysis.influence_level if decision_maker_analysis.influence_level is not None else "N/A"}</div>', unsafe_allow_html=True)
                        for evidence in decision_maker_analysis.influence_evidence:
                            st.markdown(f'<div class="meeting-item">• {evidence}</div>', unsafe_allow_html=True)

                    # Business Model & Market Synergy
                    st.markdown('<div class="meeting-header">💼 Business Alignment</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="meeting-item"><strong>Business Model Fit:</strong> {fit_result.business_model_fit if fit_result.business_model_fit is not None else "N/A"}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="meeting-item">{fit_result.business_model_analysis if fit_result.business_model_analysis is not None else "N/A"}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="meeting-item"><strong>Market Synergy:</strong> {fit_result.market_synergy if fit_result.market_synergy is not None else "N/A"}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="meeting-item">{fit_result.market_synergy_explanation if fit_result.market_synergy_explanation is not None else "N/A"}</div>', unsafe_allow_html=True)

                    # Engagement Opportunities
                    st.markdown('<div class="meeting-header">🚀 Engagement Opportunities</div>', unsafe_allow_html=True)
                    for opportunity in fit_result.engagement_opportunities:
                        st.markdown(f"""
                            <div class="agenda-item">
                                <div class="agenda-title">{opportunity.opportunity_description if opportunity.opportunity_description is not None else 'N/A'}</div>
                                <div class="meeting-item">• {opportunity.rationale if opportunity.rationale is not None else 'N/A'}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    # Potential Challenges
                    st.markdown('<div class="meeting-header">⚠️ Potential Challenges</div>', unsafe_allow_html=True)
                    for challenge in fit_result.potential_challenges:
                        st.markdown(f"""
                            <div class="agenda-item risk-item">
                                <div class="agenda-title">{challenge.challenge_description if challenge.challenge_description is not None else 'N/A'}</div>
                                <div class="meeting-item">• Impact: {challenge.impact_assessment if challenge.impact_assessment is not None else 'N/A'}</div>
                                <div class="meeting-item">• Mitigation: {challenge.mitigation_strategy if challenge.mitigation_strategy is not None else 'N/A'}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    # Recommended Approach
                    st.markdown('<div class="meeting-header">🎯 Recommended Approach</div>', unsafe_allow_html=True)
                    recommended_approach = fit_result.recommended_approach
                    if recommended_approach:
                        st.markdown(f"""
                            <div class="agenda-item success-item">
                                <div class="agenda-title">{recommended_approach.approach_description if recommended_approach.approach_description is not None else 'N/A'}</div>
                                <div class="meeting-item">• Rationale: {recommended_approach.rationale if recommended_approach.rationale is not None else 'N/A'}</div>
                                <div class="meeting-item">• Expected Outcomes: {', '.join(recommended_approach.expected_outcomes) if recommended_approach.expected_outcomes else 'N/A'}</div>
                                <div class="meeting-item">• Resources Required: {', '.join(recommended_approach.resources_required) if recommended_approach.resources_required else 'N/A'}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    # Next Steps
                    st.markdown('<div class="meeting-header">➡️ Next Steps</div>', unsafe_allow_html=True)
                    for step in fit_result.next_steps:
                        st.markdown(f"""
                            <div class="meeting-item next-step-item">• {step.step_description if step.step_description is not None else 'N/A'}
                                <div class="meeting-item" style="margin-left: 1rem;">Rationale: {step.rationale if step.rationale is not None else 'N/A'}</div>
                            </div>
                        """, unsafe_allow_html=True)

            
