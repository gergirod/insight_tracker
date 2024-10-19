import sqlite3
from datetime import datetime
from insight_tracker.profile_crew import ProfessionalProfile
from insight_tracker.company_crew import Company

def init_db():
    """
    Initialize the SQLite database and create the users table with a unique email constraint.
    """
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,  -- Ensures email is unique
            company TEXT,
            role TEXT
        )
    ''')  # Corrected the SQL syntax here
    conn.commit()
    conn.close()

def save_user_info(full_name, email, company, role):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (full_name, email, company, role)
        VALUES (?, ?, ?, ?)
    ''', (full_name, email, company, role))
    conn.commit()
    conn.close()

def getUserByEmail(email):
    """
    Retrieve a user from the database by their email address.
    """
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()  # Fetch only one user since email should be unique
    conn.close()
    return user

def update_user_info(company, role, email):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    conn.execute('''
        UPDATE users
        SET company = ?, role = ?
        WHERE email = ?
        ''', (company, role, email))  
    conn.commit()
    conn.close()


def create_user_if_not_exists(full_name, email, company, role):
    """
    Check if a user with the given email exists. If not, create a new user.
    """
    # Check if the email already exists
    user = getUserByEmail(email)
    
    if user:
        update_user_info(company, role, email)
        return False  # User already exists
    else:
        try:
            save_user_info(full_name, email, company, role)
            return True  # New user created
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
            return False  # Failed to create the user
        

# ... (existing code) ...

def init_recent_searches_db():
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    
    # Create profile_searches table
    c.execute('''
        CREATE TABLE IF NOT EXISTS profile_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            full_name TEXT,
            current_job_title TEXT,
            professional_background TEXT,
            past_jobs TEXT,
            key_achievements TEXT,
            contact TEXT,
            search_date TIMESTAMP
        )
    ''')
    
    # Create company_searches table
    c.execute('''
        CREATE TABLE IF NOT EXISTS company_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            company_name TEXT,
            company_website TEXT,
            company_summary TEXT,
            company_industry TEXT,
            company_services TEXT,
            company_industries TEXT,
            company_awards_recognitions TEXT,
            company_clients_partners TEXT,
            search_date TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_profile_search(user_email, profile):
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    c.execute('''
        INSERT INTO profile_searches 
        (user_email, full_name, current_job_title, professional_background, past_jobs, key_achievements, contact, search_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_email, profile.full_name, profile.current_job_title, profile.profesional_background, 
          profile.past_jobs, profile.key_achievements, profile.contact, current_time))
    conn.commit()
    conn.close()

def save_company_search(user_email, company):
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    c.execute('''
        INSERT INTO company_searches 
        (user_email, company_name, company_website, company_summary, company_industry, company_services, 
        company_industries, company_awards_recognitions, company_clients_partners, search_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_email, company.company_name, company.company_website, company.company_summary, 
          company.company_industry, company.company_services, company.company_industries, 
          company.company_awards_recognitions, company.company_clients_partners, current_time))
    conn.commit()
    conn.close()


def get_recent_profile_searches(user_email, limit=5):
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    c.execute('''
        SELECT full_name, current_job_title, professional_background, past_jobs, key_achievements, contact, search_date 
        FROM profile_searches
        WHERE user_email = ?
        ORDER BY search_date DESC
        LIMIT ?
    ''', (user_email, limit))
    searches = c.fetchall()
    conn.close()
    return [ProfessionalProfile(full_name=s[0], current_job_title=s[1], profesional_background=s[2], 
                                past_jobs=s[3], key_achievements=s[4], contact=s[5], search_date=s[6]) 
            for s in searches]

def get_recent_company_searches(user_email, limit=5):
    conn = sqlite3.connect('recent_searches.db')
    c = conn.cursor()
    c.execute('''
        SELECT company_name, company_website, company_summary, company_industry, company_services, 
               company_industries, company_awards_recognitions, company_clients_partners, search_date
        FROM company_searches
        WHERE user_email = ?
        ORDER BY search_date DESC
        LIMIT ?
    ''', (user_email, limit))
    searches = c.fetchall()
    conn.close()
    return [Company(company_name=s[0], company_website=s[1], company_summary=s[2], company_industry=s[3],
                    company_services=s[4], company_industries=s[5], company_awards_recognitions=s[6],
                    company_clients_partners=s[7], search_date=s[8]) 
            for s in searches]