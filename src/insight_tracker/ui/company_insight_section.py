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
from insight_tracker.db import get_user_company_info
import json
from datetime import datetime
import re

research_company = None

def inject_css():
    st.markdown("""
        <style>
        /* Base button style for all action buttons */
        .stButton > button {
            background-color: #4f46e5 !important;  /* Indigo color */
            color: white !important;
            padding: 14px 24px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            text-decoration: none !important;
            border-radius: 50px !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2) !important;
            transition: all 0.2s ease !important;
            margin: 10px 0 !important;
            letter-spacing: 0.3px !important;
            text-align: center !important;
            width: 100% !important;
        }

        /* Hover state for all buttons */
        .stButton > button:hover {
            background-color: #4338ca !important;  /* Darker indigo */
            box-shadow: 0 4px 6px rgba(79, 70, 229, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Active state */
        .stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* Disabled state */
        .stButton > button:disabled {
            background-color: #6c757d !important;
            opacity: 0.65 !important;
            cursor: not-allowed !important;
        }

        /* Save button style */
        .stButton > button:has(div:contains("💾")) {
            background-color: #28a745 !important;
            box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2) !important;
        }

        .stButton > button:has(div:contains("💾")):hover {
            background-color: #218838 !important;
            box-shadow: 0 4px 6px rgba(40, 167, 69, 0.3) !important;
        }

        /* Ensure text color stays white */
        .stButton > button div {
            color: white !important;
        }

        .meeting-header {
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            color: #1E88E5;
        }
        .meeting-item {
            margin-bottom: 0.5rem;
            padding-left: 1rem;
        }
        .risk-item {
            color: #FF5252;
        }
        .success-item {
            color: #4CAF50;
        }
        .next-step-item {
            color: #FF9800;
        }
        </style>
    """, unsafe_allow_html=True)

def run_async(coroutine):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def get_verification_badge(status):
    """Return appropriate badge based on verification status"""
    if status.lower() == 'verified':
        return "✅ Verified"
    elif status.lower() == 'not provided':
        return "❓ Not Provided"
    elif status.lower() == 'unverified':
        return "⚠️ Unverified"
    elif status.lower() == 'partial':
        return "🔄 Partially Verified"
    else:
        return f"ℹ️ {status}"

def get_verification_color(status):
    """Return appropriate color based on verification status"""
    if status.lower() == 'verified':
        return "#00CC66"  # Green
    elif status.lower() == 'not provided':
        return "#808080"  # Gray
    elif status.lower() == 'unverified':
        return "#FF6B6B"  # Red
    elif status.lower() == 'partial':
        return "#FFA500"  # Orange
    else:
        return "#4A90E2"  # Blue

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

    # Input fields for company name and industry
    company_name = st.text_input("Company to research")
    industry = st.text_input("Industry (helps focus the research)")

    # Initialize events list in session state if not exists
    if 'company_event_history' not in st.session_state:
        st.session_state.company_event_history = []

    # Research button
    if st.button("🔍 Delegate Research", 
                key="company_research_button", 
                use_container_width=True):
        if company_name and industry:
            try:
                print("Debug - UI: Starting company research stream")
                st.session_state.company_event_history = []  # Clear previous events
                
                # Create containers for live updates
                progress_container = st.empty()
                with progress_container.container():
                    agent_status = st.empty()
                    thought_status = st.empty()
                    task_status = st.empty()
                    transition_status = st.empty()
                
                # Regular synchronous iteration
                for event in insight_service.get_company_analysis_stream(
                    company_name=company_name,
                    industry=industry
                ):
                    print(f"Debug - UI got event: {event}")
                    event_type = event.get('type')
                    content = event.get('content')
                    
                    # Add event to history
                    st.session_state.company_event_history.append({
                        'type': event_type,
                        'content': content,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Update UI based on event type
                    with progress_container.container():
                        if event_type == "agent_start" and content and content.get('name') and content.get('function'):
                            # Clear previous agent's thoughts and tasks
                            thought_status.empty()
                            task_status.empty()
                            transition_status.empty()
                            
                            # Add special styling for industry researcher
                            agent_name = content['name']
                            agent_function = content['function']
                            
                            if "industry" in agent_name.lower():
                                agent_status.markdown(f"""
                                🏭 **Current Agent: {agent_name}**  
                                *{agent_function}*
                                """)
                            else:
                                agent_status.markdown(f"""
                                🤖 **Current Agent: {agent_name}**  
                                *{agent_function}*
                                """)
                            
                        elif event_type == "thought" and content:
                            thought_status.markdown(f"💭 **Thinking:**  \n{content}")
                            # Clear previous task when new thought starts
                            task_status.empty()
                            
                        elif event_type == "task_complete" and content:
                            task_status.markdown(f"✅ **Completed:**  \n{content}")
                            
                        elif event_type == "transition" and content:
                            # Clear all previous states for transition
                            agent_status.empty()
                            thought_status.empty()
                            task_status.empty()
                            transition_status.markdown(f"🔄 **Transition:**  \n{content}")
                            
                        elif event_type == "complete" and content:
                            task_status.empty()
                            if 'company_insight' in content:
                                st.session_state.company_result = content['company_insight']
                            if 'trust_evaluation' in content:
                                st.session_state.company_trust_evaluation = content['trust_evaluation']
                            st.session_state.company_search_completed = True
                            st.success("✨ Analysis Complete!")
                            break
                            
                        elif event_type == "error" and content:
                            raise Exception(content)
                    
            except Exception as e:
                print(f"Debug - Error in UI: {str(e)}")
                st.error(f"An unexpected issue occurred during research: {str(e)}")
        else:
            st.warning("Please provide both the company name and industry to begin research.")

    # Show event history right after the research button
    if st.session_state.get('company_event_history'):
        with st.expander("🕒 Analysis History", expanded=False):
            st.markdown("### Research Process Timeline")
            for event in st.session_state.company_event_history:
                event_type = event['type']
                content = event['content']
                timestamp = event['timestamp']
                
                if event_type == "agent_start":
                    agent_name = content['name']
                    agent_icon = "🏭" if "industry" in agent_name.lower() else "🤖"
                    st.markdown(f"**{timestamp}** - {agent_icon} Agent: {agent_name}")
                    st.markdown(f"*Function: {content['function']}*")
                
                elif event_type == "thought":
                    st.markdown(f"**{timestamp}** - 💭 Thinking: {content}")
                
                elif event_type == "task_complete":
                    st.markdown(f"**{timestamp}** - ✅ Completed: {content}")
                
                elif event_type == "transition":
                    st.markdown(f"**{timestamp}** - 🔄 {content}")
                
                elif event_type == "complete":
                    st.markdown(f"**{timestamp}** - ✨ Analysis Complete")
                
                elif event_type == "error":
                    st.markdown(f"**{timestamp}** - ❌ Error: {content}")
                
                st.markdown("---")

    # Display results only if research is completed
    if st.session_state.get('company_search_completed', False):
        if 'company_result' in st.session_state:
            st.markdown("---")  # Separator
            
            # Main Company Section
            st.header("📊 Company Analysis Results")
            
            # Debug output
            print(f"Debug - Company result keys: {st.session_state.company_result.keys() if st.session_state.company_result else 'None'}")
            
            # Get the company data from the result
            company_data = st.session_state.company_result
            
            # Check if we have company data
            if not company_data:
                st.warning("No company data available. The research couldn't find verifiable information.")
                return
                
            # Get company info
            company_info = company_data.get('company', {})
            
            if not company_info:
                print(f"Debug - Company data structure: {json.dumps(company_data, indent=2)}")
                st.warning("Limited company information available. The research found minimal verifiable data.")
                company_info = company_data  # Fallback to using the entire data
            
            # Get company info and industry analysis
            industry_analysis = company_data.get('industry_analysis', {})
            
            if not company_info:
                st.warning("Limited company information available. The research found minimal verifiable data.")
            
            # Basic Information Card
            st.subheader("🏢 Basic Information")
            
            # Essential info in a clean layout
            essential_fields = [
                ('company_name', '🏢 Company Name'),
                ('company_industry', '🏭 Industry'),
                ('company_website', '🌐 Website'),
                ('company_headquarters', '📍 Headquarters'),
                ('company_size', '👥 Company Size'),
                ('company_founded_year', '📅 Founded')
            ]
            
            # Check if we have any data to display
            has_data = False
            for field_key, _ in essential_fields:
                field_data = company_info.get(field_key)
                if field_data and isinstance(field_data, dict) and field_data.get('value'):
                    has_data = True
                    break
                    
            if not has_data:
                st.warning("Limited company information available. The research found minimal verifiable data.")
            
            for field_key, field_label in essential_fields:
                field_data = company_info.get(field_key, {})
                if not field_data or not isinstance(field_data, dict) or not field_data.get('value'):
                    # Skip empty fields or show as not available
                    st.markdown(f"""
                        <div style="
                            padding: 0.5rem;
                            margin-bottom: 0.5rem;
                            border-radius: 0.3rem;
                            background-color: rgba(240, 240, 240, 0.5);
                        ">
                            <div style="color: #666; font-size: 0.9em;">{field_label}</div>
                            <div style="
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                margin-top: 0.2rem;
                            ">
                                <div style="font-size: 1.1em; font-weight: 500; color: #999;">
                                    Not Available
                                </div>
                                <div style="color: #808080; font-weight: 500; font-size: 0.9em;">
                                    ❓ Not Provided
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    continue
                
                value = field_data.get('value', 'N/A')
                verification_level = field_data.get('verification_level', 'N/A')
                
                # Map verification level to badge
                if verification_level == "HIGH":
                    badge = "✅ Verified"
                    color = "#00CC66"  # Green
                elif verification_level == "MEDIUM":
                    badge = "🔄 Partially Verified"
                    color = "#FFA500"  # Orange
                elif verification_level == "LOW":
                    badge = "⚠️ Low Verification"
                    color = "#FF6B6B"  # Red
                else:
                    badge = "❓ Unknown"
                    color = "#808080"  # Gray
                
                st.markdown(f"""
                    <div style="
                        padding: 0.5rem;
                        margin-bottom: 0.5rem;
                        border-radius: 0.3rem;
                        background-color: rgba(255, 255, 255, 0.8);
                    ">
                        <div style="color: #666; font-size: 0.9em;">{field_label}</div>
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-top: 0.2rem;
                        ">
                            <div style="font-size: 1.1em; font-weight: 500;">
                                {value}
                            </div>
                            <div style="color: {color}; font-weight: 500; font-size: 0.9em;">
                                {badge}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Expandable details for each field
                with st.expander("📝 Details & Sources"):
                    # Sources
                    sources = field_data.get('source_urls', [])
                    if sources:
                        st.markdown("**🔍 Sources:**")
                        for source in sources:
                            st.markdown(f"- [{source}]({source})")
                    
                    # Verification notes
                    notes = field_data.get('verification_notes')
                    if notes:
                        st.markdown("**📋 Verification Notes:**")
                        st.markdown(f"- {notes}")
            
            # Contact Information
            st.subheader("📇 Contact Information")
            contact_fields = [
                ('company_linkedin', '🔗 LinkedIn'),
                ('company_social_media', '📱 Social Media')
            ]
            
            # Check if we have any contact data
            has_contact = False
            for field_key, _ in contact_fields:
                field_data = company_info.get(field_key)
                if field_data and isinstance(field_data, dict) and field_data.get('value'):
                    has_contact = True
                    break
                    
            if not has_contact:
                st.info("No contact information available for this company.")
            
            # Display contact fields vertically
            for field_key, field_label in contact_fields:
                field_data = company_info.get(field_key, {})
                if not field_data or not isinstance(field_data, dict) or not field_data.get('value'):
                    continue
                    
                value = field_data.get('value', 'N/A')
                verification_level = field_data.get('verification_level', 'N/A')
                
                # Map verification level to badge
                if verification_level == "HIGH":
                    badge = "✅ Verified"
                    color = "#00CC66"  # Green
                elif verification_level == "MEDIUM":
                    badge = "🔄 Partially Verified"
                    color = "#FFA500"  # Orange
                elif verification_level == "LOW":
                    badge = "⚠️ Low Verification"
                    color = "#FF6B6B"  # Red
                else:
                    badge = "❓ Unknown"
                    color = "#808080"  # Gray
                
                st.markdown(f"""
                    <div style="
                        padding: 0.5rem;
                        margin-bottom: 0.5rem;
                        border-radius: 0.3rem;
                        background-color: rgba(255, 255, 255, 0.8);
                    ">
                        <div style="color: #666; font-size: 0.9em;">{field_label}</div>
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-top: 0.2rem;
                        ">
                            <div style="font-size: 1.1em; font-weight: 500;">
                                {value}
                            </div>
                            <div style="color: {color}; font-weight: 500; font-size: 0.9em;">
                                {badge}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Expandable details for each contact field
                with st.expander("📝 Details & Sources"):
                    # Sources
                    sources = field_data.get('source_urls', [])
                    if sources:
                        st.markdown("**🔍 Sources:**")
                        for source in sources:
                            st.markdown(f"- [{source}]({source})")
                    
                    # Verification notes
                    notes = field_data.get('verification_notes')
                    if notes:
                        st.markdown("**📋 Verification Notes:**")
                        st.markdown(f"- {notes}")
            
            # Detailed Sections
            st.markdown("---")
            st.subheader("📚 Detailed Information")
            
            # Define the sections we want to display
            detailed_sections = [
                ('company_summary', 'Company Summary'),
                ('company_services', 'Products & Services'),
                ('company_industries', 'Industries Served'),
                ('company_clients_partners', 'Clients & Partners'),
                ('company_awards_recognitions', 'Awards & Recognition'),
                ('company_culture', 'Company Culture'),
                ('company_recent_updates', 'Recent Updates')
            ]
            
            # Filter out sections with no data
            available_sections = []
            for key, label in detailed_sections:
                field_data = company_info.get(key)
                if field_data:
                    # Handle both dict and list types
                    if isinstance(field_data, dict) and field_data.get('value'):
                        available_sections.append((key, label))
                    elif isinstance(field_data, list) and len(field_data) > 0:
                        available_sections.append((key, label))
            
            if not available_sections:
                st.info("No detailed information available for this company.")
            else:
                # Create tabs for available sections
                if available_sections:
                    tabs = st.tabs([label for _, label in available_sections])
                    
                    for i, (section_key, _) in enumerate(available_sections):
                        with tabs[i]:
                            section_data = company_info.get(section_key, {})
                            
                            # Handle both dict and list types
                            if isinstance(section_data, dict):
                                verification_level = section_data.get('verification_level', 'N/A')
                                
                                # Map verification level to badge
                                if verification_level == "HIGH":
                                    badge = "✅ Verified"
                                    color = "#00CC66"  # Green
                                elif verification_level == "MEDIUM":
                                    badge = "🔄 Partially Verified"
                                    color = "#FFA500"  # Orange
                                elif verification_level == "LOW":
                                    badge = "⚠️ Low Verification"
                                    color = "#FF6B6B"  # Red
                                else:
                                    badge = "❓ Unknown"
                                    color = "#808080"  # Gray
                                
                                st.markdown(f"""
                                    <div style="float: right; color: {color};">{badge}</div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(section_data.get('value', 'N/A'))
                                
                                with st.expander("🔍 Sources & Verification", expanded=False):
                                    # Sources
                                    sources = section_data.get('source_urls', [])
                                    if sources:
                                        st.markdown("**Sources:**")
                                        for source in sources:
                                            st.markdown(f"- [{source}]({source})")
                                    
                                    # Verification notes
                                    notes = section_data.get('verification_notes')
                                    if notes:
                                        st.markdown("**Verification Notes:**")
                                        st.markdown(f"- {notes}")
                            
                            elif isinstance(section_data, list):
                                for item in section_data:
                                    if isinstance(item, dict) and item.get('value'):
                                        verification_level = item.get('verification_level', 'N/A')
                                        
                                        # Map verification level to badge
                                        if verification_level == "HIGH":
                                            badge = "✅ Verified"
                                            color = "#00CC66"  # Green
                                        elif verification_level == "MEDIUM":
                                            badge = "🔄 Partially Verified"
                                            color = "#FFA500"  # Orange
                                        elif verification_level == "LOW":
                                            badge = "⚠️ Low Verification"
                                            color = "#FF6B6B"  # Red
                                        else:
                                            badge = "❓ Unknown"
                                            color = "#808080"  # Gray
                                        
                                        st.markdown(f"""
                                            <div style="
                                                padding: 0.5rem;
                                                margin-bottom: 0.5rem;
                                                border-radius: 0.3rem;
                                                background-color: rgba(255, 255, 255, 0.8);
                                            ">
                                                <div style="
                                                    display: flex;
                                                    justify-content: space-between;
                                                    align-items: center;
                                                ">
                                                    <div style="font-size: 1.1em;">
                                                        {item.get('value', 'N/A')}
                                                    </div>
                                                    <div style="color: {color}; font-weight: 500; font-size: 0.9em;">
                                                        {badge}
                                                    </div>
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)
                                        
                                        with st.expander("🔍 Sources & Verification", expanded=False):
                                            # Sources
                                            sources = item.get('source_urls', [])
                                            if sources:
                                                st.markdown("**Sources:**")
                                                for source in sources:
                                                    st.markdown(f"- [{source}]({source})")
                                            
                                            # Verification notes
                                            notes = item.get('verification_notes')
                                            if notes:
                                                st.markdown("**Verification Notes:**")
                                                st.markdown(f"- {notes}")
            
            # Add Trust Evaluation section
            if 'company_trust_evaluation' in st.session_state:
                trust_eval = st.session_state.company_trust_evaluation
                with st.expander("🔒 Trust Evaluation", expanded=False):
                    try:
                        # Trust Score
                        score_col1, score_col2 = st.columns(2)
                        with score_col1:
                            overall_score = trust_eval.get('trust_score', {}).get('overall_score', 'N/A')
                            confidence = trust_eval.get('trust_score', {}).get('confidence_level', 'N/A')
                            risk = trust_eval.get('trust_score', {}).get('risk_level', 'N/A')
                            
                            st.metric("Trust Score", f"{overall_score}%" if overall_score != 'N/A' else 'N/A')
                            st.markdown(f"**Confidence Level:** {confidence}")
                            st.markdown(f"**Risk Level:** {risk}")
                        
                        with score_col2:
                            category_scores = trust_eval.get('trust_score', {}).get('category_scores', {})
                            if category_scores:
                                st.markdown("**Category Scores:**")
                                for category, score in category_scores.items():
                                    st.markdown(f"- {category}: {score}%")
                        
                        # Supporting Evidence
                        evidence_list = trust_eval.get('supporting_evidence', [])
                        if evidence_list:
                            st.markdown("### Supporting Evidence")
                            for evidence in evidence_list:
                                with st.container():
                                    st.markdown(f"**{evidence.get('source_type', 'Unknown Source')}** "
                                              f"(Credibility: {evidence.get('credibility_score', 'N/A')}%)")
                                    st.markdown(evidence.get('description', ''))
                                    source_url = evidence.get('source_url')
                                    if source_url:
                                        st.markdown(f"*Source: [{source_url}]({source_url})*")
                        
                        # Areas of Concern
                        concerns = trust_eval.get('areas_of_concern', [])
                        if concerns:
                            st.markdown("### Areas of Concern")
                            for concern in concerns:
                                st.markdown(f"- {concern}")
                        
                        # Verification Summary
                        verification_summary = trust_eval.get('verification_summary', {})
                        if verification_summary:
                            st.markdown("### Verification Summary")
                            
                            # Handle different verification summary formats
                            if 'total_fields' in verification_summary:
                                total_fields = verification_summary.get('total_fields', 'N/A')
                                verified_fields = verification_summary.get('verified_fields', 'N/A')
                                verification_rate = verification_summary.get('verification_rate', 'N/A')
                                
                                st.markdown(f"- Total Fields: {total_fields}")
                                st.markdown(f"- Verified Fields: {verified_fields}")
                                st.markdown(f"- Verification Rate: {verification_rate}")
                            else:
                                # Alternative format
                                verification_date = verification_summary.get('verification_date', 'N/A')
                                verified_percentage = verification_summary.get('verified_fields_percentage', 'N/A')
                                
                                st.markdown(f"- Verification Date: {verification_date}")
                                st.markdown(f"- Verified Fields: {verified_percentage}")
                                
                                # Primary sources
                                primary_sources = verification_summary.get('primary_sources', [])
                                if primary_sources:
                                    st.markdown("**Primary Sources:**")
                                    for source in primary_sources:
                                        st.markdown(f"- {source}")
                            
                            # Verification notes
                            notes = verification_summary.get('notes') or verification_summary.get('overall_verification_notes')
                            if notes:
                                st.markdown(f"**Notes:** {notes}")
                                
                        # Recommendations
                        recommendations = trust_eval.get('recommendations', [])
                        if recommendations:
                            st.markdown("### Recommendations")
                            for rec in recommendations:
                                st.markdown(f"- {rec}")
                                    
                    except Exception as e:
                        print(f"Error displaying trust evaluation: {str(e)}")
                        st.warning("Some trust evaluation data could not be displayed")

            # Disable the save button
            if st.button("💾 Save Research", key="save_company_button", disabled=True):
                pass  # This code won't execute since the button is disabled
                
            # Add a note explaining why it's disabled
            st.markdown("""
                <div style="font-size: 0.8em; color: #666; text-align: center;">
                    Save functionality temporarily unavailable
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