import streamlit as st
from insight_tracker.db import get_recent_profile_searches, get_recent_company_searches
from datetime import datetime
from insight_tracker.api.models.responses import ProfessionalProfile

def inject_recent_searches_css():
    st.markdown("""
        <style>
        .recent-search-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        .recent-search-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .search-type {
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .search-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .search-subtitle {
            font-size: 14px;
            color: #555;
            margin-bottom: 5px;
        }
        .search-details {
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        }
        .search-date {
            font-size: 12px;
            color: #888;
            text-align: right;
            margin-top: 10px;
        }
        .no-searches-message {
            color: #888;
            font-style: italic;
            text-align: center;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 10px;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

def format_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
        return date_obj.strftime("%b %d, %Y")
    except ValueError:
        return "N/A"

def display_profile_search(profile : ProfessionalProfile, index):
    
    expander_title = profile.full_name or "Unknown"
    if profile.current_job_title:
        expander_title += f" - {profile.current_job_title}"
    
    with st.expander(expander_title, expanded=False):
        details = []
        if profile.professional_background:
            details.append(f"<strong>Background:</strong> {profile.professional_background}")
        if profile.past_jobs:
            details.append(f"<strong>Past Jobs:</strong> {profile.past_jobs}")
        if profile.key_achievements:
            details.append(f"<strong>Achievements:</strong> {profile.key_achievements}")
        
        details_html = "<br>".join(details) if details else "No additional details available."
        
        st.markdown(f"""
        <div class="recent-search-card">
            <div class="search-type">Profile</div>
            <div class="search-title">{profile.full_name or 'Unknown'}</div>
            <div class="search-subtitle">{profile.current_job_title or 'Unknown Role'}</div>
            <div class="search-details">
                {details_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_company_search(company, index):
    print(company)
    expander_title = company.company_name or "Unknown Company"
    if company.company_industry:
        expander_title += f" - {company.company_industry}"
    
    with st.expander(expander_title, expanded=False):
        details = []
        if company.company_website:
            details.append(f"<strong>Website:</strong> <a href='{company.company_website}' target='_blank'>{company.company_website}</a>")
        if company.company_summary:
            details.append(f"<strong>Summary:</strong> {company.company_summary}")
        if company.company_services:
            details.append(f"<strong>Services:</strong> {company.company_services}")
        if company.company_industries:
            details.append(f"<strong>Industries:</strong> {company.company_industries}")
        if company.company_awards_recognitions:
            details.append(f"<strong>Awards:</strong> {company.company_awards_recognitions}")
        if company.company_clients_partners:
            details.append(f"<strong>Clients/Partners:</strong> {company.company_clients_partners}")
        
        details_html = "<br>".join(details) if details else "No additional details available."
        
        st.markdown(f"""
        <div class="recent-search-card">
            <div class="search-type">Company</div>
            <div class="search-title">{company.company_name or 'Unknown Company'}</div>
            <div class="search-subtitle">{company.company_industry or 'Unknown Industry'}</div>
            <div class="search-details">
                {details_html}
            </div>
            <div class="search-date">{format_date(company.search_date)}</div>
        </div>
        """, unsafe_allow_html=True)

def recent_searches_section():
    inject_recent_searches_css()
    st.header("Recent Searches")

    user_email = st.session_state.user.get('email')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Profile Searches")
        profile_searches = get_recent_profile_searches(user_email, limit=5)
        if profile_searches:
            for index, profile in enumerate(profile_searches):
                print(profile)
                display_profile_search(profile, index)
        else:
            st.markdown('<div class="no-searches-message">No recent profile searches</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("Company Searches")
        company_searches = get_recent_company_searches(user_email, limit=5)
        if company_searches:
            for index, company in enumerate(company_searches):
                display_company_search(company, index)
        else:
            st.markdown('<div class="no-searches-message">No recent company searches</div>', unsafe_allow_html=True)

    if not profile_searches and not company_searches:
        st.markdown('<div class="no-searches-message">You haven\'t made any searches yet. Start by searching for a profile or company!</div>', unsafe_allow_html=True)