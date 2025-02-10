import streamlit as st
import os
import asyncio
import urllib3
from insight_tracker.db import getUserByEmail, save_profile_search, get_user_company_info, decrease_user_usage_limit
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.exceptions.api_exceptions import ApiError
import re
import logging


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

    # Initialize session state keys if they don't exist
    if 'action_states' not in st.session_state:
        st.session_state.action_states = {
            'search_completed': False,
            'action_in_progress': None,
            'errors': [],
            'warnings': [],
            'results': {},  # Store all results (email, meeting, fit)
            'last_search': None  # Store last search parameters to prevent duplicate searches
        }

    # Store insight_service in session state so it's accessible everywhere
    if 'insight_service' not in st.session_state:
        st.session_state.insight_service = insight_service

    # Input and Research section
    with st.form(key='research_form'):
        person_name = st.text_input("Name", key="person_name_input")
        person_company = st.text_input("Company", key="person_company_input")
        submit = st.form_submit_button("Research")
        
        if submit and person_name and person_company:
            # Prevent duplicate searches
            search_key = f"{person_name}-{person_company}"
            if search_key != st.session_state.action_states['last_search']:
                try:
                    with st.spinner('Analyzing profile...'):
                        profile_result = run_async(
                            insight_service.get_profile_analysis(
                                full_name=person_name,
                                company_name=person_company
                            )
                        )
                        st.session_state.profile_result = profile_result
                        st.session_state.action_states['search_completed'] = True
                        st.session_state.action_states['last_search'] = search_key
                        st.rerun()
                except Exception as e:
                    handle_error(e)
        elif submit:
            st.warning("Please provide both Name and Company.")

    # Display results and action buttons only if search is completed
    if st.session_state.action_states['search_completed'] and hasattr(st.session_state, 'profile_result'):
        display_profile_info(st.session_state.profile_result.profile)
        
        # Save Research button in its own container
        with st.container():
            if st.button("💾 Save Research", key="save_button"):
                save_profile_search(user_email, st.session_state.profile_result.profile)
                st.success("Research saved successfully!")

        # Action buttons in their own container
        with st.container():
            if not st.session_state.action_states['action_in_progress']:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Generate Email", key="generate_email_button", use_container_width=True):
                        handle_action_with_state("email")
                with col2:
                    if st.button("Prepare for Meeting", key="prepare_meeting_button", use_container_width=True):
                        handle_action_with_state("meeting")
                with col3:
                    if st.button("Evaluate Fit", key="evaluate_fit_button", use_container_width=True):
                        handle_action_with_state("fit")

        # Display results in a separate container
        with st.container():
            display_action_results()

def handle_action_with_state(action_type):
    """Wrapper to handle action state management"""
    st.session_state.action_states['action_in_progress'] = action_type
    user_email = st.session_state.user.get('email')
    user = getUserByEmail(user_email)
    user_company = get_user_company_info(user_email)
    profile = st.session_state.profile_result.profile

    try:
        if action_type == "email":
            handle_email_generation(user, user_company, profile)
        elif action_type == "meeting":
            handle_meeting_preparation(user_company, profile)
        elif action_type == "fit":
            handle_fit_evaluation(user_company, profile)
    finally:
        st.session_state.action_states['action_in_progress'] = None
        st.rerun()  # Rerun to update UI

def handle_error(error):
    """Centralized error handling"""
    if isinstance(error, ApiError):
        st.error(f"API Error: {error.error_message}")
    else:
        st.error(f"An error occurred: {str(error)}")
        logging.error(f"Error details: {type(error).__name__}", exc_info=True)
    st.session_state.action_states['search_completed'] = False

def display_profile_info(profile):
    """Separate function to handle profile information display"""
    with st.container():
        st.subheader("👤 Profile Information")
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

def display_action_results():
    """Separate function to handle all result displays"""
    # Display any errors or warnings first
    for error in st.session_state.action_states.get('errors', []):
        st.error(error)
    for warning in st.session_state.action_states.get('warnings', []):
        st.warning(warning)

    # Display action results
    results = st.session_state.action_states.get('results', {})
    
    if 'email_content' in results:
        with st.expander("✉️ Outreach Email", expanded=False):
            clean_email = re.sub(r'<[^>]+>', '', results['email_content'])
            st.markdown(clean_email, unsafe_allow_html=True)

    if 'meeting_result' in results:
        display_meeting_results(results['meeting_result'])

    if 'fit_result' in results:
        display_fit_results(results['fit_result'])

def handle_email_generation(user, user_company, profile):
    if not user or not user_company:
        warning_message = []
        if not user:
            warning_message.append("• Complete your personal information (name, role, company)")
        if not user_company:
            warning_message.append("• Add your company information")
        st.session_state.action_states['warnings'].append(f"⚠️ Additional information required:\n{chr(10).join(warning_message)}")
        st.session_state.nav_bar_option_selected = "Settings"
        st.rerun()
    
    try:
        with st.spinner('Generating outreach email...'):
            sender_info = {
                "full_name": user[1],
                "company": user[4],
                "role": user[3]
            }
            profile_data = profile.__dict__
            email_content = run_async(
                st.session_state.insight_service.generate_outreach_email(
                    profile=profile_data,
                    company=user_company.__dict__,
                    sender_info=sender_info
                )
            )
            st.session_state.action_states['results']['email_content'] = email_content
            st.success("Email generated successfully!")
    except Exception as e:
        st.session_state.action_states['errors'].append(f"Failed to generate email: {str(e)}")

def handle_meeting_preparation(user_company, profile):
    if not user_company:
        st.session_state.action_states['warnings'].append("⚠️ Company information required for meeting preparation")
        st.session_state.nav_bar_option_selected = "Settings"
        st.rerun()
    
    try:
        with st.spinner('Preparing meeting strategy...'):
            meeting_result = run_async(
                st.session_state.insight_service.prepare_meeting(
                    profile=profile.__dict__,
                    company=user_company.__dict__
                )
            )
            st.session_state.action_states['results']['meeting_result'] = meeting_result
            st.success("Meeting preparation completed!")
    except Exception as e:
        st.session_state.action_states['errors'].append(f"Failed to prepare meeting: {str(e)}")

def handle_fit_evaluation(user_company, profile):
    if not user_company:
        st.session_state.action_states['warnings'].append("⚠️ Company information required for fit evaluation")
        st.session_state.nav_bar_option_selected = "Settings"
        st.rerun()
    
    try:
        with st.spinner('Evaluating fit...'):
            fit_result = run_async(
                st.session_state.insight_service.evaluate_profile_fit(
                    profile=profile.__dict__,
                    company=user_company.__dict__
                )
            )
            st.session_state.action_states['results']['fit_result'] = fit_result
            st.success("Fit evaluation completed!")
    except Exception as e:
        st.session_state.action_states['errors'].append(f"Failed to evaluate fit: {str(e)}")

def display_meeting_results(meeting_prep):
    """Display meeting preparation results"""
    with st.expander("📅 Meeting Preparation", expanded=False):
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

def display_fit_results(fit_result):
    """Display fit evaluation results"""
    with st.expander("🔍 Fit Evaluation Results", expanded=False):
        evaluation = fit_result.evaluation

        # Fit Score and Summary
        st.markdown('<div class="meeting-header">📊 Overall Fit Assessment</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meeting-item"><strong>Fit Score:</strong> {evaluation.fit_score if evaluation.fit_score is not None else "N/A"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meeting-item"><strong>Summary:</strong> {evaluation.fit_summary if evaluation.fit_summary is not None else "N/A"}</div>', unsafe_allow_html=True)

        # Key Insights
        st.markdown('<div class="meeting-header">💡 Key Insights</div>', unsafe_allow_html=True)
        for insight in evaluation.key_insights:
            st.markdown(f'<div class="meeting-item">• {insight}</div>', unsafe_allow_html=True)

        # Expertise Matches
        if evaluation.expertise_matches:
            st.markdown('<div class="meeting-header">🎯 Expertise Matches</div>', unsafe_allow_html=True)
            for match in evaluation.expertise_matches:
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
        if evaluation.decision_maker_analysis:
            st.markdown(f'<div class="meeting-item"><strong>Influence Level:</strong> {evaluation.decision_maker_analysis.influence_level if evaluation.decision_maker_analysis.influence_level is not None else "N/A"}</div>', unsafe_allow_html=True)
            for evidence in evaluation.decision_maker_analysis.influence_evidence:
                st.markdown(f'<div class="meeting-item">• {evidence}</div>', unsafe_allow_html=True)

        # Business Model & Market Synergy
        st.markdown('<div class="meeting-header">💼 Business Alignment</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meeting-item"><strong>Business Model Fit:</strong> {evaluation.business_model_fit if evaluation.business_model_fit is not None else "N/A"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meeting-item">{evaluation.business_model_analysis if evaluation.business_model_analysis is not None else "N/A"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meeting-item"><strong>Market Synergy:</strong> {evaluation.market_synergy if evaluation.market_synergy is not None else "N/A"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meeting-item">{evaluation.market_synergy_explanation if evaluation.market_synergy_explanation is not None else "N/A"}</div>', unsafe_allow_html=True)

        # Engagement Opportunities
        st.markdown('<div class="meeting-header">🚀 Engagement Opportunities</div>', unsafe_allow_html=True)
        for opportunity in evaluation.engagement_opportunities:
            st.markdown(f"""
                <div class="agenda-item">
                    <div class="agenda-title">{opportunity.opportunity_description if opportunity.opportunity_description is not None else 'N/A'}</div>
                    <div class="meeting-item">• {opportunity.rationale if opportunity.rationale is not None else 'N/A'}</div>
                </div>
            """, unsafe_allow_html=True)

        # Potential Challenges
        st.markdown('<div class="meeting-header">⚠️ Potential Challenges</div>', unsafe_allow_html=True)
        for challenge in evaluation.potential_challenges:
            st.markdown(f"""
                <div class="agenda-item risk-item">
                    <div class="agenda-title">{challenge.challenge_description if challenge.challenge_description is not None else 'N/A'}</div>
                    <div class="meeting-item">• Impact: {challenge.impact_assessment if challenge.impact_assessment is not None else 'N/A'}</div>
                    <div class="meeting-item">• Mitigation: {challenge.mitigation_strategy if challenge.mitigation_strategy is not None else 'N/A'}</div>
                </div>
            """, unsafe_allow_html=True)

        # Recommended Approach
        st.markdown('<div class="meeting-header">🎯 Recommended Approach</div>', unsafe_allow_html=True)
        if evaluation.recommended_approach:
            st.markdown(f"""
                <div class="agenda-item success-item">
                    <div class="agenda-title">{evaluation.recommended_approach.approach_description if evaluation.recommended_approach.approach_description is not None else 'N/A'}</div>
                    <div class="meeting-item">• Rationale: {evaluation.recommended_approach.rationale if evaluation.recommended_approach.rationale is not None else 'N/A'}</div>
                    <div class="meeting-item">• Expected Outcomes: {', '.join(evaluation.recommended_approach.expected_outcomes) if evaluation.recommended_approach.expected_outcomes else 'N/A'}</div>
                    <div class="meeting-item">• Resources Required: {', '.join(evaluation.recommended_approach.resources_required) if evaluation.recommended_approach.resources_required else 'N/A'}</div>
                </div>
            """, unsafe_allow_html=True)

        # Next Steps
        st.markdown('<div class="meeting-header">➡️ Next Steps</div>', unsafe_allow_html=True)
        for step in evaluation.next_steps:
            st.markdown(f"""
                <div class="meeting-item next-step-item">• {step.step_description if step.step_description is not None else 'N/A'}
                    <div class="meeting-item" style="margin-left: 1rem;">Rationale: {step.rationale if step.rationale is not None else 'N/A'}</div>
                </div>
            """, unsafe_allow_html=True)

            
