import sqlite3
from datetime import datetime
from typing import List, Optional
from insight_tracker.api.models.responses import ProfessionalProfile, Company
def init_db():
    """Initialize the SQLite database and create the users table"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,
            company TEXT,
            role TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_recent_searches_db():
    """Initialize the recent searches database"""
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    
    # Create profile_searches table matching ProfessionalProfile model
    c.execute('''
        CREATE TABLE IF NOT EXISTS profile_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            full_name TEXT NOT NULL,
            current_company TEXT,
            current_company_url TEXT,
            current_job_title TEXT,
            current_company TEXT,
            current_company_url TEXT,
            professional_background TEXT,
            past_jobs TEXT,
            key_achievements TEXT,
            contact TEXT,
            linkedin_url TEXT,
            search_date TIMESTAMP
        )
    ''')
    
    # Create company_searches table matching Company model
    c.execute('''
        CREATE TABLE IF NOT EXISTS company_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            company_name TEXT NOT NULL,
            company_website TEXT,
            company_linkedin TEXT,
            company_summary TEXT,
            company_industry TEXT,
            company_size TEXT,
            company_services TEXT,
            company_industries TEXT,
            company_awards_recognitions TEXT,
            company_clients_partners TEXT,
            company_founded_year INTEGER,
            company_headquarters TEXT,
            company_culture TEXT,
            company_recent_updates TEXT,
            search_date TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_profile_search(user_email: str, profile: ProfessionalProfile, company: str) -> None:
    """Save profile search to database"""
    conn = sqlite3.connect('recent_searches.db')
    cursor = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute("""
            INSERT INTO profile_searches 
            (user_email, full_name, current_job_title, current_company, current_company_url, professional_background, past_jobs, key_achievements, contact, linkedin_url, search_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_email,
            profile.full_name,
            profile.current_job_title,
            profile.current_company,
            profile.current_company_url,
            profile.professional_background,
            profile.past_jobs,
            profile.key_achievements,
            profile.contact,
            profile.linkedin_url,
            current_time
        ))
        conn.commit()
    except Exception as e:
        print(f"Error saving profile search: {e}")
        raise
    finally:
        conn.close()

def save_company_search(user_email: str, company: Company) -> None:
    """Save company search to database"""
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    # Convert lists to strings for storage
    company_services = ','.join(company.company_services) if company.company_services else None
    company_industries = ','.join(company.company_industries) if company.company_industries else None
    company_awards = ','.join(company.company_awards_recognitions) if company.company_awards_recognitions else None
    company_clients = ','.join(company.company_clients_partners) if company.company_clients_partners else None
    company_culture = ','.join(company.company_culture) if company.company_culture else None
    company_updates = ','.join(company.company_recent_updates) if company.company_recent_updates else None
    
    c.execute('''
        INSERT INTO company_searches (
            user_email, company_name, company_website, company_linkedin,
            company_summary, company_industry, company_size,
            company_services, company_industries, company_awards_recognitions,
            company_clients_partners, company_founded_year, company_headquarters,
            company_culture, company_recent_updates, search_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_email,
        company.company_name,
        company.company_website,
        company.company_linkedin,
        company.company_summary,
        company.company_industry,
        company.company_size,
        company_services,
        company_industries,
        company_awards,
        company_clients,
        company.company_founded_year,
        company.company_headquarters,
        company_culture,
        company_updates,
        current_time
    ))
    
    conn.commit()
    conn.close()

def get_recent_profile_searches(user_email: str, limit: int = 5) -> List[ProfessionalProfile]:
    """Get recent profile searches from database"""
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT full_name, current_job_title, current_company, current_company_url, professional_background,
               past_jobs, key_achievements, contact, linkedin_url
        FROM profile_searches
        WHERE user_email = ?
        ORDER BY search_date DESC
        LIMIT ?
    ''', (user_email, limit))
    
    searches = c.fetchall()
    conn.close()
    
    return [
        ProfessionalProfile(
            full_name=row[0],
            current_job_title=row[1],
            current_company=row[2],
            current_company_url=row[3],
            professional_background=row[4],
            past_jobs=row[5],
            key_achievements=row[6],
            contact=row[7],
            linkedin_url=row[6]
        )
        for row in searches
    ]

def get_recent_company_searches(user_email: str, limit: int = 5) -> List[Company]:
    """Get recent company searches from database"""
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT company_name, company_website, company_linkedin, company_summary,
               company_industry, company_size, company_services, company_industries,
               company_awards_recognitions, company_clients_partners,
               company_founded_year, company_headquarters, company_culture,
               company_recent_updates
        FROM company_searches
        WHERE user_email = ?
        ORDER BY search_date DESC
        LIMIT ?
    ''', (user_email, limit))
    
    searches = c.fetchall()
    conn.close()
    
    return [
        Company(
            company_name=row[0],
            company_website=row[1],
            company_linkedin=row[2],
            company_summary=row[3],
            company_industry=row[4],
            company_size=row[5],
            company_services=row[6].split(',') if row[6] else None,
            company_industries=row[7].split(',') if row[7] else None,
            company_awards_recognitions=row[8].split(',') if row[8] else None,
            company_clients_partners=row[9].split(',') if row[9] else None,
            company_founded_year=row[10],
            company_headquarters=row[11],
            company_culture=row[12].split(',') if row[12] else None,
            company_recent_updates=row[13].split(',') if row[13] else None
        )
        for row in searches
    ]

# User management functions remain unchanged
def save_user_info(full_name: str, email: str, company: str, role: str) -> None:
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (full_name, email, company, role)
        VALUES (?, ?, ?, ?)
    ''', (full_name, email, company, role))
    conn.commit()
    conn.close()

def getUserByEmail(email: str) -> Optional[tuple]:
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_info(company: str, role: str, email: str) -> None:
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET company = ?, role = ?
        WHERE email = ?
    ''', (company, role, email))
    conn.commit()
    conn.close()

def create_user_if_not_exists(full_name, email, company="", role=""):
    """
    Creates a user if they don't exist.
    Returns: (bool, bool) - (success, is_new_user)
    """
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    try:
        # Check if user exists
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_user = c.fetchone()
        
        if existing_user:
            return True, False  # User exists, not new
        
        # Create new user
        c.execute('''
            INSERT INTO users (name, email, role, company)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, role, company))
        conn.commit()
        return True, True  # User created, is new
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, False
    finally:
        conn.close()

def alter_profile_searches_table():
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    
    # Add the new columns
    c.execute('ALTER TABLE profile_searches ADD COLUMN current_company TEXT')
    c.execute('ALTER TABLE profile_searches ADD COLUMN current_company_url TEXT')
    
    conn.commit()
    conn.close()

def init_user_company_db():
    """Initialize the SQLite database for user company information"""
    conn = sqlite3.connect('user_company_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT UNIQUE,
            company_name TEXT,
            company_website TEXT,
            company_linkedin TEXT,
            company_summary TEXT,
            company_industry TEXT,
            company_size TEXT,
            company_services TEXT,
            company_industries TEXT,
            company_awards_recognitions TEXT,
            company_clients_partners TEXT,
            company_founded_year INTEGER,
            company_headquarters TEXT,
            company_culture TEXT,
            company_recent_updates TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_company_info(user_email: str, company: Company) -> None:
    """Save user company information to the database"""
    conn = sqlite3.connect('user_company_data.db')
    c = conn.cursor()
    
    # Convert lists to strings for storage
    company_services = ','.join(company.company_services) if company.company_services else None
    company_industries = ','.join(company.company_industries) if company.company_industries else None
    company_awards = ','.join(company.company_awards_recognitions) if company.company_awards_recognitions else None
    company_clients = ','.join(company.company_clients_partners) if company.company_clients_partners else None
    company_culture = ','.join(company.company_culture) if company.company_culture else None
    company_updates = ','.join(company.company_recent_updates) if company.company_recent_updates else None
    
    try:
        c.execute('''
            INSERT INTO user_companies (
                user_email, company_name, company_website, company_linkedin,
                company_summary, company_industry, company_size,
                company_services, company_industries, company_awards_recognitions,
                company_clients_partners, company_founded_year, company_headquarters,
                company_culture, company_recent_updates
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_email) DO UPDATE SET
                company_name=excluded.company_name,
                company_website=excluded.company_website,
                company_linkedin=excluded.company_linkedin,
                company_summary=excluded.company_summary,
                company_industry=excluded.company_industry,
                company_size=excluded.company_size,
                company_services=excluded.company_services,
                company_industries=excluded.company_industries,
                company_awards_recognitions=excluded.company_awards_recognitions,
                company_clients_partners=excluded.company_clients_partners,
                company_founded_year=excluded.company_founded_year,
                company_headquarters=excluded.company_headquarters,
                company_culture=excluded.company_culture,
                company_recent_updates=excluded.company_recent_updates
        ''', (
            user_email,
            company.company_name,
            company.company_website,
            company.company_linkedin,
            company.company_summary,
            company.company_industry,
            company.company_size,
            company_services,
            company_industries,
            company_awards,
            company_clients,
            company.company_founded_year,
            company.company_headquarters,
            company_culture,
            company_updates
        ))
        conn.commit()
    except Exception as e:
        print(f"Error saving user company info: {e}")
        raise
    finally:
        conn.close()

def get_user_company_info(user_email: str) -> Optional[Company]:
    """Retrieve user company information from the database"""
    conn = sqlite3.connect('user_company_data.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT company_name, company_website, company_linkedin, company_summary,
               company_industry, company_size, company_services, company_industries,
               company_awards_recognitions, company_clients_partners,
               company_founded_year, company_headquarters, company_culture,
               company_recent_updates
        FROM user_companies
        WHERE user_email = ?
    ''', (user_email,))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return Company(
            company_name=row[0],
            company_website=row[1],
            company_linkedin=row[2],
            company_summary=row[3],
            company_industry=row[4],
            company_size=row[5],
            company_services=row[6].split(',') if row[6] else None,
            company_industries=row[7].split(',') if row[7] else None,
            company_awards_recognitions=row[8].split(',') if row[8] else None,
            company_clients_partners=row[9].split(',') if row[9] else None,
            company_founded_year=row[10],
            company_headquarters=row[11],
            company_culture=row[12].split(',') if row[12] else None,
            company_recent_updates=row[13].split(',') if row[13] else None
        )
    return None
