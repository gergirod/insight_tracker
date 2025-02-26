import streamlit as st
import os
import asyncio
import urllib3
from insight_tracker.db import getUserByEmail, save_profile_search, get_recent_profile_searches, get_user_company_info
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.exceptions.api_exceptions import ApiError
import re
from streamlit.runtime.scriptrunner import add_script_run_ctx
from datetime import datetime


# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_async(coroutine):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def inject_css():
    # First override Streamlit's default theme
    st.markdown("""
        <style>
        /* Override Streamlit's default theme */
        :root {
            --primary-color: #0d6efd;
            --background-color: #ffffff;
            --secondary-background-color: #f8f9fa;
            --text-color: #212529;
        }
        
        /* Reset all button styles first */
        .stButton > button {
            all: unset;
            width: 100% !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            cursor: pointer !important;
            text-align: center !important;
            font-family: sans-serif !important;
            font-size: 1rem !important;
            margin-top: 1rem !important;
            display: block !important;
            box-sizing: border-box !important;
        }
        
        /* Research button specific */
        .stButton > button:has(div:contains("Research")) {
            background-color: #4f46e5 !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2) !important;
        }

        .stButton > button:has(div:contains("Research")):hover {
            background-color: #4338ca !important;
            box-shadow: 0 4px 6px rgba(79, 70, 229, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Save button */
        .stButton > button:has(div:contains("💾")) {
            background-color: #28a745 !important;
        }
        
        /* Action buttons */
        .stButton > button[type="primary"] {
            background-color: #0d6efd !important;
        }

        /* Ensure text color stays white */
        .stButton > button div {
            color: white !important;
        }
        
        /* Disabled state */
        .stButton > button:disabled {
            background-color: #6c757d !important;
            opacity: 0.65 !important;
            cursor: not-allowed !important;
        }

        /* Style for all action buttons */
        .stButton > button {
            background-color: #1E88E5 !important;
            color: white !important;
            padding: 14px 24px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            border-radius: 50px !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease !important;
            margin: 10px 0 !important;
            letter-spacing: 0.3px !important;
            text-align: center !important;
            width: 100% !important;
        }

        .stButton > button:hover {
            background-color: #1976D2 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            transform: translateY(-1px) !important;
        }

        .stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* Save button style */
        .stButton > button:has(div:contains("💾")) {
            background-color: #28a745 !important;
        }

        /* Ensure text color stays white */
        .stButton > button div {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def get_verification_badge(status):
    """Return appropriate badge based on verification status"""
    if status.lower() == 'verified':
        return "✅ Verified"
    elif status.lower() == 'not provided' or status.lower() == 'Verified (No information available)':
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

def profile_insight_section():
    inject_css()
    st.header("Profile Insight")
    
    user_email = st.session_state.user.get('email')
    
    # Initialize API service
    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )
    insight_service = InsightService(api_client)

    # Input fields
    name = st.text_input("Name of the person you want to research")
    company = st.text_input("Their company")

    # Create placeholders for updates
    if 'status_placeholder' not in st.session_state:
        st.session_state.status_placeholder = st.empty()
    
    # Initialize events list in session state if not exists
    if 'event_history' not in st.session_state:
        st.session_state.event_history = []

    # Display all events stored in session state
    for event in st.session_state.event_history:
        event_type = event.get('type')
        content = event.get('content')
        timestamp = event.get('timestamp')
        
        if event_type == "agent_start":
            st.write(f"🤖 **Agent:** {content['name']}")
            st.write(f"*Function: {content['function']}*")
        elif event_type == "thought":
            st.write(f"💭 {content}")
        elif event_type == "task_complete":
            st.write(f"✅ {content}")
        elif event_type == "transition":
            st.write(f"🔄 {content}")
        elif event_type == "complete":
            st.write(f"✨ Analysis Complete")
        elif event_type == "error":
            st.write(f"❌ Error: {content}")

    async def process_stream():
        try:
            async for event in insight_service.get_profile_analysis_stream(
                full_name=name,
                company_name=company
            ):
                print(f"UI received event: {event}")
                # Add event to session state
                st.session_state.event_history.append({
                    'type': event.get('type'),
                    'content': event.get('content'),
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                if event.get('type') == 'complete':
                    st.session_state.profile_result = event['content']['profile_insight']
                    st.session_state.search_completed = True
                    return
                
                # Force a rerun to update the UI
                st.rerun()
                
        except Exception as e:
            print(f"Stream processing error: {e}")
            raise

    # Research button
    if st.button("🔍 Delegate Research", key="research_button", use_container_width=True):
        if name and company:
            try:
                print("Debug - UI: Starting research stream")
                st.session_state.event_history = []  # Clear previous events
                
                # Create containers for live updates
                progress_container = st.empty()
                with progress_container.container():
                    agent_status = st.empty()
                    thought_status = st.empty()
                    task_status = st.empty()
                    transition_status = st.empty()
                
                # Regular synchronous iteration
                for event in insight_service.get_profile_analysis_stream(
                    full_name=name,
                    company_name=company
                ):
                    print(f"Debug - UI got event: {event}")
                    event_type = event.get('type')
                    content = event.get('content')
                    
                    # Add event to history
                    st.session_state.event_history.append({
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
                            
                            agent_status.markdown(f"""
                            🤖 **Current Agent: {content['name']}**  
                            *{content['function']}*
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
                            if 'profile_insight' in content:
                                st.session_state.profile_result = content['profile_insight']
                            if 'trust_evaluation' in content:
                                st.session_state.trust_evaluation = content['trust_evaluation']
                            st.session_state.search_completed = True
                            st.success("✨ Analysis Complete!")
                            break
                            
                        elif event_type == "error" and content:
                            raise Exception(content)
                    
            except Exception as e:
                print(f"Debug - Error in UI: {str(e)}")
                st.error(f"An unexpected issue occurred during research: {str(e)}")
        else:
            st.warning("Please provide both the name and company to begin research.")

    # Show event history right after the research button
    if st.session_state.get('event_history'):
        with st.expander("🕒 Analysis History", expanded=False):
            st.markdown("### Research Process Timeline")
            for event in st.session_state.event_history:
                event_type = event['type']
                content = event['content']
                timestamp = event['timestamp']
                
                if event_type == "agent_start":
                    st.markdown(f"**{timestamp}** - 🤖 Agent: {content['name']}")
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
    if st.session_state.get('search_completed', False):
        if 'profile_result' in st.session_state:
            st.markdown("---")  # Separator
            
            st.subheader("👤 Basic Information")
            profile = st.session_state.profile_result
            
            # Essential info in a clean layout
            essential_fields = [
                ('full_name', '👤 Name'),
                ('current_job_title', '💼 Title'),
                ('current_company', '🏢 Company'),
                ('current_company_industry', '🏭 Industry')
            ]
            
            for field_key, field_label in essential_fields:
                field_data = profile.get(field_key, {})
                
                # Handle both dictionary and list types
                if isinstance(field_data, dict):
                    value = field_data.get('value', 'N/A')
                    status = field_data.get('verification_status', 'N/A')
                    badge = get_verification_badge(status)
                    color = get_verification_color(status)
                    
                    st.markdown(f"""
                        <div style="
                            padding: 0.5rem;
                            margin-bottom: 0.5rem;
                            border-radius: 0.3rem;
                            background-color: rgba(255, 255, 255, 0.8);
                            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
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
                        cols = st.columns([2, 1])
                        with cols[0]:
                            sources = field_data.get('source_url', [])
                            if sources:
                                st.markdown("**🔍 Sources:**")
                                for source in sources:
                                    st.markdown(f"- [{source}]({source})")
                        
                        with cols[1]:
                            credibility = field_data.get('source_credibility', [])
                            if credibility:
                                st.markdown("**⭐ Credibility:**")
                                for cred in credibility:
                                    st.markdown(f"- {cred}")
                
                # Handle list type fields
                elif isinstance(field_data, list):
                    st.markdown(f"### {field_label}")
                    for item in field_data:
                        if isinstance(item, dict):
                            value = item.get('value', 'N/A')
                            status = item.get('verification_status', 'N/A')
                            badge = get_verification_badge(status)
                            color = get_verification_color(status)
                            
                            st.markdown(f"""
                                <div style="
                                    padding: 0.5rem;
                                    margin-bottom: 0.5rem;
                                    border-radius: 0.3rem;
                                    background-color: rgba(255, 255, 255, 0.8);
                                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                                ">
                                    <div style="
                                        display: flex;
                                        justify-content: space-between;
                                        align-items: center;
                                    ">
                                        <div style="font-size: 1.1em;">
                                            {value}
                                        </div>
                                        <div style="color: {color}; font-weight: 500; font-size: 0.9em;">
                                            {badge}
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Expandable details for each item
                            with st.expander("📝 Details & Sources"):
                                cols = st.columns([2, 1])
                                with cols[0]:
                                    sources = item.get('source_url', [])
                                    if sources:
                                        st.markdown("**🔍 Sources:**")
                                        for source in sources:
                                            st.markdown(f"- [{source}]({source})")
                                
                                with cols[1]:
                                    credibility = item.get('source_credibility', [])
                                    if credibility:
                                        st.markdown("**⭐ Credibility:**")
                                        for cred in credibility:
                                            st.markdown(f"- {cred}")
            
            # Contact Information
            st.subheader("📇 Contact Information")
            contact_fields = [
                ('contact', '📧 Contact'),
                ('linkedin_url', '🔗 LinkedIn')
            ]
            
            # Display contact fields vertically
            for field_key, field_label in contact_fields:
                field_data = profile.get(field_key, {})
                value = field_data.get('value', 'N/A')
                status = field_data.get('verification_status', 'N/A')
                badge = get_verification_badge(status)
                color = get_verification_color(status)
                
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
                    cols = st.columns([2, 1])
                    with cols[0]:
                        sources = field_data.get('source_url', [])
                        if sources:
                            st.markdown("**🔍 Sources:**")
                            for source in sources:
                                st.markdown(f"- [{source}]({source})")
                    
                    with cols[1]:
                        credibility = field_data.get('source_credibility', [])
                        if credibility:
                            st.markdown("**⭐ Credibility:**")
                            for cred in credibility:
                                st.markdown(f"- {cred}")
            
            # Detailed Sections
            st.markdown("---")
            st.subheader("📚 Detailed Information")
            
            tabs = st.tabs([
                "Professional Background",
                "Past Experience",
                "Key Achievements"
            ])
            
            sections = ['professional_background', 'past_jobs', 'key_achievements']
            for tab, section in zip(tabs, sections):
                with tab:
                    section_data = profile.get(section, {})
                    status = section_data.get('verification_status', 'N/A')
                    badge = get_verification_badge(status)
                    color = get_verification_color(status)
                    
                    st.markdown(f"""
                        <div style="float: right; color: {color};">{badge}</div>
                    """, unsafe_allow_html=True)
                    
                    # Special handling for achievements
                    if section == 'key_achievements':
                        try:
                            # Try to parse industry profile for structured achievements
                            industry_profile = profile.get('industry_profile', {}).get('value', '{}')
                            if isinstance(industry_profile, str):
                                import json
                                try:
                                    industry_data = json.loads(industry_profile)
                                    if 'Achievements' in industry_data:
                                        st.markdown("### 🏆 Verified Achievements")
                                        for achievement in industry_data['Achievements']:
                                            # Create achievement card
                                            st.markdown(f"""
                                                <div style="
                                                    padding: 1rem;
                                                    margin-bottom: 1rem;
                                                    background-color: rgba(255, 255, 255, 0.8);
                                                    border-radius: 0.5rem;
                                                    border-left: 4px solid {get_verification_color('verified')};
                                                ">
                                                    <div style="
                                                        display: flex;
                                                        justify-content: space-between;
                                                        align-items: center;
                                                    ">
                                                        <div style="font-weight: 600; color: #1a1a1a;">
                                                            {achievement.get('Type', 'Achievement')}
                                                        </div>
                                                        <div style="color: #00CC66;">✅</div>
                                                    </div>
                                                    <div style="margin: 0.5rem 0;">
                                                        {achievement.get('Details', '')}
                                                    </div>
                                                    <div style="text-align: right;">
                                                        <a href="{achievement.get('Link', '#')}" target="_blank" style="color: #4A90E2; text-decoration: none;">
                                                            🔗 View Source
                                                        </a>
                                                    </div>
                                                </div>
                                            """, unsafe_allow_html=True)
                                except json.JSONDecodeError:
                                    # Fall back to regular achievement display
                                    pass
                            
                            # Display any remaining achievements from the main value field
                            achievements_text = section_data.get('value', '')
                            achievements = [ach.strip() for ach in achievements_text.split(';') if ach.strip()]
                            
                            if achievements:
                                st.markdown("### Additional Achievements")
                                for achievement in achievements:
                                    has_source = any(source in achievement for source in section_data.get('source_url', []))
                                    verification_icon = "✅" if has_source else "⚠️"
                                    st.markdown(f"""
                                        <div style="
                                            display: flex;
                                            justify-content: space-between;
                                            align-items: center;
                                            padding: 0.5rem;
                                            margin-bottom: 0.5rem;
                                            background-color: rgba(255, 255, 255, 0.5);
                                            border-radius: 0.3rem;
                                        ">
                                            <div>{achievement}</div>
                                            <div>{verification_icon}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                        except Exception as e:
                            print(f"Error parsing achievements: {e}")
                            # Fall back to displaying raw value
                            st.markdown(section_data.get('value', 'N/A'))
                    else:
                        st.markdown(section_data.get('value', 'N/A'))
                    
                    with st.expander("🔍 Sources & Verification"):
                        sources = section_data.get('source_url', [])
                        if sources:
                            st.markdown("**Sources:**")
                            for source in sources:
                                st.markdown(f"- [{source}]({source})")
                        
                        credibility = section_data.get('source_credibility', [])
                        if credibility:
                            st.markdown("**Credibility Assessment:**")
                            for cred in credibility:
                                st.markdown(f"- {cred}")

            # Add Trust Evaluation section
            if 'trust_evaluation' in st.session_state:
                trust_eval = st.session_state.trust_evaluation
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
                            total_fields = verification_summary.get('total_fields_verified', 'N/A')
                            st.markdown(f"- Total Fields Verified: {total_fields}")
                            
                            methods = verification_summary.get('verification_methods_used', [])
                            if methods:
                                st.markdown("**Verification Methods:**")
                                for method in methods:
                                    st.markdown(f"- {method}")
                                    
                    except Exception as e:
                        print(f"Error displaying trust evaluation: {str(e)}")
                        st.warning("Some trust evaluation data could not be displayed")

            # Disable the save button
            if st.button("💾 Save Research", key="save_button", disabled=True):
                pass  # This code won't execute since the button is disabled
                
            # Add a note explaining why it's disabled
            st.markdown("""
                <div style="font-size: 0.8em; color: #666; text-align: center;">
                    Save functionality temporarily unavailable
                </div>
            """, unsafe_allow_html=True)

            # Action buttons
            st.markdown("### 🚀 Actions")
            
            # Create three columns for the action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Disable the button by adding disabled=True
                st.button("✉️ Request Outreach Draft", 
                         type="primary",
                         key="request_email_button",
                         use_container_width=True,
                         disabled=True)
                
                # Add a note explaining why it's disabled
                st.markdown("""
                    <div style="font-size: 0.8em; color: #666; text-align: center;">
                        Feature temporarily unavailable
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                # Disable the button
                st.button("📅 Generate Meeting Brief", 
                         type="primary",
                         key="prepare_meeting_button",
                         use_container_width=True,
                         disabled=True)
                
                # Add a note explaining why it's disabled
                st.markdown("""
                    <div style="font-size: 0.8em; color: #666; text-align: center;">
                        Feature temporarily unavailable
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                # Disable the button
                st.button("⚖️ Analyze Partnership Fit", 
                         type="primary",
                         key="evaluate_fit_button",
                         use_container_width=True,
                         disabled=True)
                
                # Add a note explaining why it's disabled
                st.markdown("""
                    <div style="font-size: 0.8em; color: #666; text-align: center;">
                        Feature temporarily unavailable
                    </div>
                """, unsafe_allow_html=True)

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

            
