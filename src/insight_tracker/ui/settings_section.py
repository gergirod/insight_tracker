import streamlit as st
from insight_tracker.db import create_user_if_not_exists, save_user_company_info
from insight_tracker.api.client.insight_client import InsightApiClient
from insight_tracker.api.services.insight_service import InsightService
from insight_tracker.api.exceptions.api_exceptions import ApiError
import os
import asyncio
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_async(coroutine):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def inject_settings_css():
    st.markdown("""
        <style>
        .small-text {
            font-size: 14px;
            color: #4f4f4f;
            line-height: 1.5;
            margin-bottom: 8px;
        }
        
        .section-header {
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            margin-top: 10px;
            margin-bottom: 2px;
        }
        
        .container {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            background-color: #fafafa;
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
        .stButton > button:has(div:contains("Save")) {
            background-color: #28a745;
        }
        
        .stButton > button:has(div:contains("Save")):hover,
        .stButton > button:has(div:contains("Save")):active,
        .stButton > button:has(div:contains("Save")):focus {
            background-color: #218838;
            color: white !important;
        }

        /* Ensure button text stays white in all states */
        .stButton > button > div {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def display_company_data(company):
    st.markdown("<h2>🏢 Company Information</h2>", unsafe_allow_html=True)
    
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

def settings_section(user, user_company):
    st.header("Settings")

    inject_settings_css()  # Inject CSS for styling

    # Initialize API service with SSL verification disabled
    api_client = InsightApiClient(
        base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verify_ssl=False
    )
    insight_service = InsightService(api_client)

    full_name_value = user[1] if user is not None else ""
    contact_info = user[2] if user is not None else ""
    role_position_value = user[3] if user is not None else ""
    company_value = user[4] if user is not None else ""

    # Input fields for the user settings
    full_name = st.text_input("Full Name", placeholder="Enter your full name", value=full_name_value)
    email = st.text_input("Email", value=contact_info, disabled=True)
    role_position = st.text_input("Role/Position", placeholder="Enter your role or position", value=role_position_value)
    company = st.text_input("Company", placeholder="Enter your company name", value=company_value)

    # New input fields for company data
    st.subheader("Company Information")

    # Method selection
    search_method = st.radio(
        "Select how to fetch company data:",
        options=["By URL", "By Name and Industry"],
        index=0
    )

    if search_method == "By URL":
        company_url = st.text_input("Company URL", placeholder="Enter the company URL for scraping")
    else:
        company_name = st.text_input("Company Name", placeholder="Enter the company's name")
        company_industry = st.text_input("Industry", placeholder="Enter the company's industry")

    # Display existing company data if available
    if user_company is not None:
        st.markdown("### Existing Company Information")
        display_company_data(user_company)

    if st.button("Fetch Company Data", key="fetch_company_data_button"):
        try:
            with st.spinner('Fetching company data...'):
                if search_method == "By URL" and company_url:
                    company_result = run_async(
                        insight_service.get_company_analysis_by_url(
                            company_url=company_url
                        )
                    )
                elif search_method == "By Name and Industry" and company_name and company_industry:
                    company_result = run_async(
                        insight_service.get_company_analysis(
                            company_name=company_name,
                            industry=company_industry
                        )
                    )
                else:
                    st.warning("Please provide the required information based on the selected method.")
                    return

                st.session_state.company_result = company_result
                st.success("Company data fetched successfully!")
        except ApiError as e:
            st.error(f"API Error: {e.error_message}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error(f"Error details: {type(e).__name__}")

    # Display company data
    if 'company_result' in st.session_state:
        display_company_data(st.session_state.company_result.company)

    # Layout for the buttons
    col1, col2 = st.columns([1, 1])

    # Save button
    with col1:
        if st.button("Save", key="save_button"):
            # Simulate saving the data (this could be saving to a database or file)
            st.success(f"Settings saved! \nName: {full_name} \nRole: {role_position} \nCompany: {company}")
            # Store the settings in session state (this allows you to reuse the settings elsewhere in the app)
            st.session_state['full_name'] = full_name
            st.session_state['role_position'] = role_position
            st.session_state['company'] = company

            email = st.session_state.user.get('email')
            create_user_if_not_exists(full_name, email, role_position, company)

    # Save company data
    with col2:
        if st.button("💾 Save Company Data", key="save_company_data_button"):
            if 'company_result' in st.session_state:
                save_user_company_info(email, st.session_state.company_result.company)
                st.success("Company data saved successfully!")
            else:
                st.warning("No company data to save. Please fetch company data first.")