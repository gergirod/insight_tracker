import streamlit as st
import os
import asyncio
import warnings
import urllib3
from insight_tracker.db import getUserByEmail, save_profile_search, get_recent_profile_searches, get_user_company_info
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

            # Optional Proposal URL field
            st.markdown("### Optional")
            proposal_url = st.text_input("Proposal URL", key="proposal_url_input", 
                                       help="Add a proposal URL to include in the outreach email")

            # Action buttons in horizontal layout
            col1, col2, col3 = st.columns(3)
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

            with col3:
                evaluate_fit = st.button("Evaluate Fit")
                if evaluate_fit:
                    with st.spinner('Evaluating fit...'):
                        fit_result = run_async(
                            insight_service.evaluate_profile_fit(
                                profile_data=profile.__dict__,
                                company_data=get_user_company_info(user_email).__dict__
                            )
                        )
                        st.session_state.fit_evaluation_result = fit_result
                        st.success("Fit evaluation completed!")
                    

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

        # Fit Evaluation Results
        if 'fit_evaluation_result' in st.session_state:
            with st.expander("🔍 Fit Evaluation Results", expanded=False):
                fit_result = st.session_state.fit_evaluation_result.evaluation

                # Display fit score and summary
                st.markdown(f"**Fit Score:** {fit_result.get('fit_score', 'N/A')}")
                st.markdown(f"**Summary:** {fit_result.get('fit_summary', 'N/A')}")

                # Key Insights
                st.markdown("### Key Insights")
                for insight in fit_result.get('key_insights', []):
                    st.markdown(f"- {insight}")

                # Expertise Matches
                st.markdown("### Expertise Matches")
                for match in fit_result.get('expertise_matches', []):
                    st.markdown(f"- **Area:** {match.get('area', 'N/A')}")
                    st.markdown(f"  - Relevance Score: {match.get('relevance_score', 'N/A')}")
                    st.markdown(f"  - Description: {match.get('description', 'N/A')}")
                    st.markdown(f"  - Evidence: {', '.join(match.get('evidence', []))}")
                    st.markdown(f"  - Target Company Alignment: {match.get('target_company_alignment', 'N/A')}")
                    st.markdown(f"  - My Company Alignment: {match.get('my_company_alignment', 'N/A')}")
                    st.markdown(f"  - Score Explanation: {match.get('score_explanation', 'N/A')}")

                # Decision Maker Analysis
                st.markdown("### Decision Maker Analysis")
                decision_maker_analysis = fit_result.get('decision_maker_analysis', {})
                st.markdown(f"**Influence Level:** {decision_maker_analysis.get('influence_level', 'N/A')}")
                for evidence in decision_maker_analysis.get('influence_evidence', []):
                    st.markdown(f"- {evidence}")

                # Business Model Fit
                st.markdown("### Business Model Fit")
                st.markdown(f"**Score:** {fit_result.get('business_model_fit', 'N/A')}")
                st.markdown(f"**Analysis:** {fit_result.get('business_model_analysis', 'N/A')}")

                # Market Synergy
                st.markdown("### Market Synergy")
                st.markdown(f"**Score:** {fit_result.get('market_synergy', 'N/A')}")
                st.markdown(f"**Explanation:** {fit_result.get('market_synergy_explanation', 'N/A')}")

                # Company Alignments
                st.markdown("### Company Alignments")
                for alignment in fit_result.get('company_alignments', []):
                    st.markdown(f"- **Area:** {alignment.get('area', 'N/A')}")
                    st.markdown(f"  - Strength: {alignment.get('strength', 'N/A')}")
                    st.markdown(f"  - Description: {alignment.get('description', 'N/A')}")
                    st.markdown(f"  - Evidence: {', '.join(alignment.get('evidence', []))}")
                    st.markdown(f"  - Impact Potential: {alignment.get('impact_potential', 'N/A')}")

                # Engagement Opportunities
                st.markdown("### Engagement Opportunities")
                for opportunity in fit_result.get('engagement_opportunities', []):
                    st.markdown(f"- **Opportunity:** {opportunity.get('opportunity', 'N/A')}")
                    st.markdown(f"  - Evidence: {opportunity.get('evidence', 'N/A')}")

                # Growth Potential
                st.markdown("### Growth Potential")
                for growth in fit_result.get('growth_potential', []):
                    st.markdown(f"- **Potential:** {growth.get('potential', 'N/A')}")
                    st.markdown(f"  - Evidence: {growth.get('evidence', 'N/A')}")

                # Cultural Alignment
                st.markdown("### Cultural Alignment")
                for alignment in fit_result.get('cultural_alignment', []):
                    st.markdown(f"- **Factor:** {alignment.get('factor', 'N/A')}")
                    st.markdown(f"  - Evidence: {alignment.get('evidence', 'N/A')}")

                # Potential Challenges
                st.markdown("### Potential Challenges")
                for challenge in fit_result.get('potential_challenges', []):
                    st.markdown(f"- **Challenge:** {challenge.get('challenge', 'N/A')}")
                    st.markdown(f"  - Evidence: {challenge.get('evidence', 'N/A')}")

                # Risk Analysis
                st.markdown("### Risk Analysis")
                st.markdown(f"{fit_result.get('risk_analysis', 'N/A')}")

                # Recommended Approach
                st.markdown("### Recommended Approach")
                recommended_approach = fit_result.get('recommended_approach', {})
                st.markdown(f"**Approach:** {recommended_approach.get('approach', 'N/A')}")
                st.markdown(f"**Justification:** {recommended_approach.get('justification', 'N/A')}")

                # Priority Level
                st.markdown("### Priority Level")
                st.markdown(f"**Level:** {fit_result.get('priority_level', 'N/A')}")
                st.markdown(f"**Justification:** {fit_result.get('priority_justification', 'N/A')}")

                # Next Steps
                st.markdown("### Next Steps")
                for step in fit_result.get('next_steps', []):
                    st.markdown(f"- **Step:** {step.get('step', 'N/A')}")
                    st.markdown(f"  - Description: {step.get('description', 'N/A')}")

                # Competitive Analysis
                st.markdown("### Competitive Analysis")
                st.markdown(f"{fit_result.get('competitive_analysis', 'N/A')}")

                # Long Term Potential
                st.markdown("### Long Term Potential")
                st.markdown(f"{fit_result.get('long_term_potential', 'N/A')}")

                # Resource Implications
                st.markdown("### Resource Implications")
                st.markdown(f"{fit_result.get('resource_implications', 'N/A')}")

        if st.button("💾 Save Research", key="save_button"):
            save_profile_search(user_email, profile, person_company)
            st.success("Research saved successfully!")
            
