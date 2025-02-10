import streamlit as st
import pandas as pd
from insight_tracker.db import getUserByEmail, save_company_search, get_recent_company_searches
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.models.requests import CompanyInsightRequest, ProfileInsightRequest
from insight_tracker.api.exceptions.api_exceptions import ApiError
from insight_tracker.api.models.responses import Company
import asyncio
import os
from insight_tracker.api.models.responses import Company
from insight_tracker.db import get_user_company_info, decrease_user_usage_limit

research_company = None

def inject_css():
    st.markdown("""
        <style>
        /* Modern Radio Button Styling */
        .stRadio > label {
            display: none;  /* Hide the default label */
        }
        
        .stRadio > div {
            display: flex;
            gap: 15px;
            margin-top: 1rem;
            margin-bottom: 2rem;
        }
        
        /* Hide the default radio button circle */
        .stRadio input[type="radio"] {
            display: none !important;
        }
        
        .stRadio > div > div {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px 25px;
            cursor: pointer;
            transition: all 0.2s ease;
            flex: 1;
            text-align: center;
            color: #495057;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stRadio > div > div:hover {
            background-color: #f8f9fa;
            border-color: #0d6efd;
            color: #0d6efd;
        }
        
        .stRadio > div > div[data-value="true"] {
            background-color: #e7f1ff;
            color: #0d6efd;
            border-color: #0d6efd;
            font-weight: 500;
        }

        /* View selector specific styling */
        div[data-testid="stHorizontalBlock"] .stRadio > div {
            gap: 10px;
        }

        div[data-testid="stHorizontalBlock"] .stRadio > div > div {
            padding: 10px 20px;
        }
        
        /* Input field styling */
        .stTextInput > div > div {
            border-radius: 8px;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            background-color: #007bff;
            color: white !important;
            border: none;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover,
        .stButton > button:active,
        .stButton > button:focus {
            background-color: #0056b3;
            border: none;
            color: white !important;
        }
        
        /* Save button specific styling */
        .stButton > button:has(div:contains("💾")) {
            background-color: #28a745;
        }
        
        .stButton > button:has(div:contains("💾")):hover,
        .stButton > button:has(div:contains("💾")):active,
        .stButton > button:has(div:contains("💾")):focus {
            background-color: #218838;
            color: white !important;
        }
        
        /* Checkbox styling */
        .stCheckbox > label {
            color: #495057;
        }
        
        .stCheckbox > div > div > div {
            background-color: #007bff;
        }

        /* Ensure button text stays white in all states */
        .stButton > button > div {
            color: white !important;
        }

        /* Search Method Radio Button Styling */
        div[data-testid="stRadio"] > div {
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        }
        
        div[data-testid="stRadio"] > div > div > div {
            background-color: white;
            border: 1px solid #e9ecef;
            padding: 10px 20px;
            border-radius: 8px;
            color: #495057;
            font-weight: 400;
            transition: all 0.2s ease;
        }
        
        div[data-testid="stRadio"] > div > div > div:hover {
            background-color: #f8f9fa;
            border-color: #0d6efd;
            color: #0d6efd;
        }
        
        div[data-testid="stRadio"] > div > div > div[aria-checked="true"] {
            background-color: #e7f1ff;
            color: #0d6efd;
            border-color: #0d6efd;
            font-weight: 500;
        }
        
        /* Hide the default radio button */
        div[data-testid="stRadio"] input[type="radio"] {
            display: none;
        }

        /* Enhanced Input Container */
        .search-container {
            background: white;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }
        
        /* Input Group Styling */
        .input-group {
            margin-bottom: 1.5rem;
        }
        
        .input-label {
            font-size: 0.9rem;
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .input-description {
            font-size: 0.85rem;
            color: #666;
            margin-top: 4px;
            margin-bottom: 8px;
        }
        
        /* Enhanced Input Styling */
        .stTextInput > div > div {
            padding: 8px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div:focus-within {
            border-color: #1E88E5;
            box-shadow: 0 0 0 3px rgba(30,136,229,0.1);
        }
        
        /* Search Method Selector */
        .search-method {
            margin-bottom: 2rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        /* Checkbox styling */
        .stCheckbox {
            background: white;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        /* Button styling */
        .stButton > button {
            padding: 0.75rem 1.5rem;
            background: linear-gradient(45deg, #1E88E5, #1976D2);
            border: none;
            color: white;
            font-weight: 500;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(45deg, #1976D2, #1565C0);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transform: translateY(-1px);
        }
        
        /* Radio button enhancement */
        .stRadio > div {
            gap: 1rem;
        }
        
        .stRadio > div > div {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            transition: all 0.2s ease;
        }
        
        .stRadio > div > div:hover {
            border-color: #1E88E5;
            background: #f8f9fa;
        }
        
        .stRadio > div > div[data-value="true"] {
            background: #e3f2fd;
            border-color: #1E88E5;
            color: #1E88E5;
        }
        </style>
    """, unsafe_allow_html=True)

def run_async(coroutine):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def company_insight_section():
    inject_css()
    st.header("Company Insight")
    
    user_email = st.session_state.user.get('email')

    # Initialize API client and service
    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )
    insight_service = InsightService(api_client)

    # Ensure search_method is in session state
    if 'search_method' not in st.session_state:
        st.session_state.search_method = 'Search by Name and Industry'

    # Define callback function for radio button
    def on_search_method_change():
        st.session_state.search_method = st.session_state.search_method_radio

    # Search method selection with enhanced UI
    st.markdown("""
        <div class="search-method">
            <div class="input-label">🔍 Search Method</div>
            <div class="input-description">Choose how you want to search for company information</div>
        </div>
    """, unsafe_allow_html=True)
    
    search_options = ["Search by Name and Industry", "Search by Company URL"]
    st.radio(
        "",
        options=search_options,
        key="search_method_radio",
        index=search_options.index(st.session_state.get('search_method', 'Search by Name and Industry')),
        on_change=on_search_method_change,
        label_visibility="collapsed"
    )

    # Display input fields based on the selected search method
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    if st.session_state.get('search_method') == "Search by Name and Industry":
        # Company Name Input
        st.markdown("""
            <div class="input-group">
                <div class="input-label">🏢 Company Name</div>
                <div class="input-description">Enter the name of the company you want to research</div>
            </div>
        """, unsafe_allow_html=True)
        company_name = st.text_input("", key="company_name_input", label_visibility="collapsed")
        
        # Industry Input
        st.markdown("""
            <div class="input-group">
                <div class="input-label">🏭 Industry</div>
                <div class="input-description">Specify the company's primary industry</div>
            </div>
        """, unsafe_allow_html=True)
        industry = st.text_input("", key="industry_input", label_visibility="collapsed")
        
    else:
        # Company URL Input
        st.markdown("""
            <div class="input-group">
                <div class="input-label">🌐 Company URL</div>
                <div class="input-description">Enter the company's website URL (e.g., https://company.com)</div>
            </div>
        """, unsafe_allow_html=True)
        company_url = st.text_input("", key="company_url_input", label_visibility="collapsed")

    # Research Options
    st.markdown("""
        <div class="input-group">
            <div class="input-label">🎯 Research Options</div>
            <div class="input-description">Additional research parameters</div>
        </div>
    """, unsafe_allow_html=True)
    research_employees = st.checkbox('Research Employees', value=False)

    st.markdown('</div>', unsafe_allow_html=True)

    # Action Buttons
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔍 Research Company", use_container_width=True):
            handle_research()
    with col2:
        if st.button("💾 Save Results", use_container_width=True):
            handle_save()

    # Save Company Search Button - Only show after successful search
    if st.session_state.get('search_completed', False):
        if st.session_state.company_data:
            company = st.session_state.company_data
            st.markdown("<h2>🏢 Company Information</h2>", unsafe_allow_html=True)
            # Store company data in session state
            st.session_state.company_data = company

            cols = st.columns(2)  # Create two columns for layout

            with cols[0]:
                st.markdown(f"**🏷️ Company Name:** {company.company_name}")
                st.markdown(f"**🌐 Website:** {company.company_website or 'N/A'}")
                st.markdown(f"**🔗 LinkedIn:** [{company.company_linkedin}]({company.company_linkedin})" if company.company_linkedin else "N/A")
                st.markdown(f"**📝 Summary:** {company.company_summary or 'N/A'}")
                st.markdown(f"**🏭 Industry:** {company.company_industry or 'N/A'}")
                st.markdown(f"**👥 Size:** {company.company_size or 'N/A'}")

            with cols[1]:
                st.markdown(f"**🛠️ Services:** {', '.join(company.company_services) if company.company_services else 'N/A'}")
                st.markdown(f"**🏢 Industries:** {', '.join(company.company_industries) if company.company_industries else 'N/A'}")
                st.markdown(f"**🏆 Awards:** {', '.join(company.company_awards_recognitions) if company.company_awards_recognitions else 'N/A'}")
                st.markdown(f"**🤝 Clients:** {', '.join(company.company_clients_partners) if company.company_clients_partners else 'N/A'}")
                st.markdown(f"**📍 Headquarters:** {company.company_headquarters or 'N/A'}")
                st.markdown(f"**📅 Founded:** {company.company_founded_year or 'N/A'}")
                st.markdown(f"**🌱 Culture:** {', '.join(company.company_culture) if company.company_culture else 'N/A'}")
                st.markdown(f"**📰 Recent Updates:** {', '.join(company.company_recent_updates) if company.company_recent_updates else 'N/A'}")

        if st.button("💾 Save Company Search"):
            if st.session_state.company_data:  # Ensure company data exists
                save_company_search(user_email, st.session_state.company_data)
                st.success("Company search saved successfully!")
            else:
                st.warning("No company data to save.")

        # Add Evaluate Fit Button
        evaluate_fit = st.button("Evaluate Fit", type="primary")
        if evaluate_fit:
            # Get latest company data
            research_company = st.session_state.company_data
            user_company = get_user_company_info(user_email)
            if not user_company:
                st.warning("""
                    ⚠️ Company information required
                    
                    To evaluate company fit, we need your company context. Please complete your company information in the Settings section first.
                    
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
                                targetCompany=research_company.__dict__,
                                company=user_company.__dict__
                            )
                        )
                        st.session_state.fit_evaluation_result = fit_result
                        st.success("Fit evaluation completed!")
                except Exception as e:
                    st.error(f"Failed to evaluate fit: {str(e)}")

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


def display_people_data():
    if not st.session_state.employee_profiles:
        return

    view_option = st.radio(
        "Select View",
        options=["List View", "Table View"],
        index=0
    )

    st.markdown("### 👥 Employee Profiles")

    if view_option == "Table View":
        # Convert profiles to DataFrame
        profiles_data = []
        for profile in st.session_state.employee_profiles:
            profiles_data.append({
                'Name': profile.full_name,
                'Title': profile.current_job_title,
                'Background': profile.professional_background,
                'Contact': profile.contact,
                'LinkedIn': profile.linkedin_url
            })
        st.dataframe(pd.DataFrame(profiles_data))
    else:
        for profile in st.session_state.employee_profiles:
            with st.expander(f"📋 {profile.full_name}"):
                if profile.current_job_title:
                    st.markdown(f"**Current Title:** {profile.current_job_title}")
                if profile.professional_background:
                    st.markdown(f"**Background:** {profile.professional_background}")
                if profile.past_jobs:
                    st.markdown(f"**Past Jobs:** {profile.past_jobs}")
                if profile.key_achievements:
                    st.markdown(f"**Key Achievements:** {profile.key_achievements}")
                if profile.contact:
                    st.markdown(f"**Contact:** {profile.contact}")
                if profile.linkedin_url:
                    st.markdown(f"**LinkedIn:** [{profile.linkedin_url}]({profile.linkedin_url})")

# Add this to handle async operations with Streamlit
def init():
    import asyncio
    if "company_insight_section" not in st.session_state:
        st.session_state.company_insight_section = asyncio.new_event_loop()

    loop = st.session_state.company_insight_section
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(company_insight_section())