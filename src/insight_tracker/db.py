import sqlite3

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
        print(f"User with email {email} updated successfully!")
        return False  # User already exists
    else:
        try:
            save_user_info(full_name, email, company, role)
            print(f"User with email {email} created successfully!")
            return True  # New user created
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
            return False  # Failed to create the user
