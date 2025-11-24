import sqlite3
import hashlib, secrets
from .db import DB_PATH
from datetime import datetime
import re

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_db():
    """
    Initializes the user database by creating the 'users' table if it doesn't exist.
    (Matches the new schema: id INTEGER PK, password TEXT)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username: str, password: str, email: str):
    """
    Registers a new user. Returns True on success, or an error string on failure.
    (Matches the new return signature)
    """
    if not username or not password or not email:
        return "All fields are required."
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    if not is_valid_email(email):
        return "Invalid email format."
        
    hashed = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
            (username.lower(), hashed, email.lower(), created_at) # Store username/email as lowercase for uniqueness check
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        if "username" in str(e).lower():
            return "Username already exists"
        elif "email" in str(e).lower():
            return "Email already exists"
        return "An unknown database error occurred"
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticates a user based on their username and password.
    
    CRITICAL FIX: Changed return signature from bool to (bool, str) 
    to return the username (result[1]) needed for Streamlit session state.
    
    Returns: (True, username) if valid, (False, error_message) otherwise.
    """
    
    if not username or not password:
        return False, "Please enter both username and password."
        
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Query uses the stored hashed column name 'password'
    c.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (username.lower(), hashed))
    result = c.fetchone()
    conn.close()
    
    if result is not None:
        # result[1] contains the username (used for session state)
        return True, result[1] 
    else:
        return False, "Invalid username or password."

def is_valid_email(email):
    """Check if the email address is valid."""
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_pattern, email) is not None

def generate_reset_token():
    """Generates a secure, random token for password reset logic."""
    return secrets.token_urlsafe(32)

def reset_user_password(email: str, new_password: str) -> bool:
    """
    Updates the user's password in the database.
    """
    hashed = hash_password(new_password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Update uses the stored hashed column name 'password'
    c.execute("UPDATE users SET password = ? WHERE email = ?", (hashed, email.lower()))
    conn.commit()
    updated = c.rowcount > 0
    conn.close()
    return updated

def get_user_by_username(username: str):
    """Retrieves user details by username."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE username = ?",
            (username.lower(),)
        )
        user_data = cursor.fetchone()
        conn.close()
        return user_data
    except Exception:
        return None