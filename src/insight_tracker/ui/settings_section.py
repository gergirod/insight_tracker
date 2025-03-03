import streamlit as st
from insight_tracker.db import create_user_if_not_exists, save_user_company_info
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.exceptions.api_exceptions import ApiError
import os
import asyncio
import urllib3
from datetime import datetime

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

        /* Save button style - keeping green but matching the new style */
        .stButton > button:has(div:contains("Save")),
        .stButton > button:has(div:contains("Update")) {
            background-color: #28a745 !important;
            box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2) !important;
        }

        .stButton > button:has(div:contains("Save")):hover,
        .stButton > button:has(div:contains("Update")):hover {
            background-color: #218838 !important;
            box-shadow: 0 4px 6px rgba(40, 167, 69, 0.3) !important;
        }

        /* Ensure text color stays white */
        .stButton > button div {
            color: white !important;
        }

        /* Input field styling */
        .stTextInput > div > div {
            border-radius: 4px !important;
        }

        /* Add spacing between input fields */
        .stTextInput {
            margin-bottom: 0.5rem !important;
        }

        /* Ensure consistent button styling */
        [data-testid="stButton"] > button {
            background-color: #0d6efd !important;  /* Bootstrap blue */
            color: white !important;
        }

        [data-testid="stButton"] > button:hover {
            background-color: #0b5ed7 !important;  /* Darker blue */
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def display_company_data(company):
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏢 Company Information</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="company-data-grid">', unsafe_allow_html=True)
    
    # Company Basic Info
    data_items = [
        ("Company Name", company.company_name, "🏷️"),
        ("Website", company.company_website or "N/A", "🌐"),
        ("Industry", company.company_industry or "N/A", "🏭"),
        ("Size", company.company_size or "N/A", "👥"),
        ("Headquarters", company.company_headquarters or "N/A", "📍"),
        ("Founded", company.company_founded_year or "N/A", "📅")
    ]
    
    for label, value, icon in data_items:
        st.markdown(f"""
            <div class="data-item">
                <div class="data-label">{icon} {label}</div>
                <div class="data-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Company Details
    if company.company_summary:
        st.markdown("""
            <div class="data-item" style="grid-column: 1 / -1;">
                <div class="data-label">📝 Company Summary</div>
                <div class="data-value">{}</div>
            </div>
        """.format(company.company_summary), unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def settings_section(user, user_company, setup_complete=True):
    inject_css()
    
    # Personal Information Section
    st.markdown("""
        <div style="margin-bottom: 32px;">
            <h2 style="
                color: #1E88E5;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                👤 Personal Information
            </h2>
            <p style="
                color: #666;
                margin-bottom: 24px;
                font-size: 0.95rem;
            ">
                Your profile information is managed through your authentication provider.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display user information in a clean card
    full_name_value = user[1] if user is not None else ""
    contact_info = user[2] if user is not None else ""
    
    st.markdown(f"""
    <div style="
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    ">
        <h3 style="margin-top: 0;">User Details</h3>
        <p><strong>Name:</strong> {full_name_value}</p>
        <p><strong>Email:</strong> {contact_info}</p>
    </div>
    """, unsafe_allow_html=True)

    # Add spacing between sections
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    # Company Information Section - matching style with Personal Information
    st.markdown("""
        <div style="margin-bottom: 32px;">
            <h2 style="
                color: #1E88E5;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                🏢 Company Information
            </h2>
            <p style="
                color: #666;
                margin-bottom: 24px;
                font-size: 0.95rem;
            ">
                Help us understand your company context to provide better insights for your professional outreach.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Company search inputs - using name and industry
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input(
            "Company Name",
            placeholder="Enter company name",
            help="Enter the name of your company"
        )
    
    with col2:
        industry = st.text_input(
            "Industry",
            placeholder="Enter industry",
            help="Enter your company's industry"
        )

    # Company Information Update Button - Full width
    if st.button("🔍 Research Company Information",
                key="research_company_info",
                use_container_width=True):
        if company_name and industry:
            try:
                with st.spinner('Researching company data...'):
                    # Initialize API client
                    api_client = InsightApiClient(
                        base_url=os.getenv('API_BASE_URL'),
                        api_key=os.getenv('API_KEY'),
                        openai_api_key=os.getenv('OPENAI_API_KEY'),
                        verify_ssl=False
                    )
                    insight_service = InsightService(api_client=api_client)
                    
                    # Create containers for live updates
                    progress_container = st.empty()
                    with progress_container.container():
                        agent_status = st.empty()
                        thought_status = st.empty()
                        task_status = st.empty()
                        transition_status = st.empty()
                    
                    # Use streaming API with the new my_company_insight endpoint
                    st.session_state.company_event_history = []
                    
                    # Use the new my_company_insight stream method
                    for event in insight_service.get_my_company_insight_stream(
                        company_name=company_name,
                        industry=industry
                    ):
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
                                if 'company_insight' in content:
                                    st.session_state.company_result = content
                                    email = st.session_state.user.get('email')
                                    save_user_company_info(email, content)
                                st.session_state.company_search_completed = True
                                st.success("✨ Company Analysis Complete!")
                                progress_container.empty()
                                break
                                
                            elif event_type == "error" and content:
                                raise Exception(content)
                
                st.rerun()  # Rerun to display the results
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
        else:
            st.warning("Please enter both company name and industry.")

    # Display current company information if available
    if st.session_state.get('company_search_completed', False) and 'company_result' in st.session_state:
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        # Get the company data from the result
        company_result = st.session_state.company_result
        
        print("company_result")
        print(company_result)
        
        # Extract company data from the correct path in the response
        company_data = None
        
        # Try all possible paths to find the company data
        if isinstance(company_result, dict):
            # Path 1: content -> company_insight -> company
            if ('content' in company_result and 
                isinstance(company_result['content'], dict) and
                'company_insight' in company_result['content'] and
                isinstance(company_result['content']['company_insight'], dict) and
                'company' in company_result['content']['company_insight']):
                company_data = company_result['content']['company_insight']['company']
                print("Found data in content.company_insight.company")
            
            # Path 2: company_insight -> company
            elif ('company_insight' in company_result and 
                  isinstance(company_result['company_insight'], dict) and
                  'company' in company_result['company_insight']):
                company_data = company_result['company_insight']['company']
                print("Found data in company_insight.company")
            
            # Path 3: content -> company_insight (no company level)
            elif ('content' in company_result and 
                  isinstance(company_result['content'], dict) and
                  'company_insight' in company_result['content']):
                company_data = company_result['content']['company_insight']
                print("Found data in content.company_insight")
            
            # Path 4: company_insight (no company level)
            elif 'company_insight' in company_result:
                company_data = company_result['company_insight']
                print("Found data in company_insight")
            
            # Path 5: Use the result itself
            else:
                company_data = company_result
                print("Using entire result as company data")
        
        print("Company data structure:")
        print(company_data)
        
        # If we have company data, display it
        if company_data:
            # Display simplified company information
            st.markdown("""
            <div style="
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            ">
                <h3 style="margin-top: 0;">Company Details</h3>
            """, unsafe_allow_html=True)
            
            # Extract basic information safely
            try:
                # Company name
                company_name = "N/A"
                if 'company_name' in company_data and isinstance(company_data['company_name'], dict):
                    company_name = company_data['company_name'].get('value', 'N/A')
                st.markdown(f"<p><strong>Name:</strong> {company_name}</p>", unsafe_allow_html=True)
                
                # Website
                website = "N/A"
                if 'company_website' in company_data and isinstance(company_data['company_website'], dict):
                    website = company_data['company_website'].get('value', 'N/A')
                
                if website != 'N/A' and isinstance(website, str) and website.startswith(('http://', 'https://')):
                    st.markdown(f"<p><strong>Website:</strong> <a href='{website}' target='_blank'>{website}</a></p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p><strong>Website:</strong> {website}</p>", unsafe_allow_html=True)
                
                # Industry
                industry = "N/A"
                if 'company_industry' in company_data and isinstance(company_data['company_industry'], dict):
                    industry = company_data['company_industry'].get('value', 'N/A')
                st.markdown(f"<p><strong>Industry:</strong> {industry}</p>", unsafe_allow_html=True)
                
                # Summary
                summary = "N/A"
                if 'company_summary' in company_data and isinstance(company_data['company_summary'], dict):
                    summary = company_data['company_summary'].get('value', 'N/A')
                st.markdown(f"<p><strong>Summary:</strong> {summary}</p>", unsafe_allow_html=True)
                
                # Services - completely defensive approach
                st.markdown("<p><strong>Services:</strong></p>", unsafe_allow_html=True)
                
                # Try different ways to access services
                services_found = False
                
                # Try company_services as a key
                if 'company_services' in company_data:
                    services = company_data['company_services']
                    services_found = True
                # Try services as a key
                elif 'services' in company_data:
                    services = company_data['services']
                    services_found = True
                # Try products_and_services as a key
                elif 'products_and_services' in company_data:
                    services = company_data['products_and_services']
                    services_found = True
                
                if services_found and services:
                    # Handle list of services
                    if isinstance(services, list):
                        for service in services:
                            if service is None:
                                continue
                            if isinstance(service, dict) and 'value' in service:
                                st.markdown(f"• {service['value']}")
                            else:
                                st.markdown(f"• {str(service)}")
                    # Handle single service as dict
                    elif isinstance(services, dict) and 'value' in services:
                        st.markdown(f"• {services['value']}")
                    # Handle string
                    elif isinstance(services, str):
                        st.markdown(f"• {services}")
                else:
                    st.markdown("• No services information available")
                
            except Exception as e:
                st.error(f"Error displaying company data: {str(e)}")
                import traceback
                st.write("Error details:", traceback.format_exc())
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add custom services/products
            st.subheader("Add Additional Information")
            
            # Add service
            new_service = st.text_input("Add Service", placeholder="Enter a service your company provides")
            if st.button("➕ Add Service", key="add_service"):
                if new_service:
                    if 'custom_services' not in st.session_state:
                        st.session_state.custom_services = []
                    st.session_state.custom_services.append(new_service)
                    st.success(f"Added service: {new_service}")
                    st.rerun()
            
            # Display custom services
            if 'custom_services' in st.session_state and st.session_state.custom_services:
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                st.markdown("<p><strong>Custom Services:</strong></p>", unsafe_allow_html=True)
                for i, service in enumerate(st.session_state.custom_services):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"• {service}")
                    with col2:
                        if st.button("🗑️", key=f"delete_service_{i}"):
                            st.session_state.custom_services.pop(i)
                            st.rerun()