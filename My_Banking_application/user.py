# user.py
import sqlite3
import random
import re
import bcrypt
import time
from database import get_connection

# Validation regexes
FULLNAME_RE = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+){0,2}$')  
USERNAME_RE = re.compile(r'^[A-Za-z0-9_]{3,20}$')
PASSWORD_RE = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,30}$')

def _generate_account_number():
    return "{:08d}".format(random.randint(0, 99999999))

def _is_account_number_unique(account_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE account_number = ?", (account_number,))
    exists = c.fetchone() is not None
    conn.close()
    return not exists

def _make_unique_account_number():
    # loop until we find a unique 8-digit account number
    for _ in range(50):
        acc = _generate_account_number()
        if _is_account_number_unique(acc):
            return acc
    raise RuntimeError("Could not generate unique account number; try again later.")

def validate_full_name(name):
    if not isinstance(name, str):
        return False, "Full name must be text."
    name = name.strip()
    if not (4 <= len(name) <= 255):
        return False, "Full name must be between 4 and 255 characters."
    if not FULLNAME_RE.match(name):
        return False, "Full name must contain only alphabets and spaces, and be 1-3 words (first, optional middle, optional last)."
    return True, None

def validate_username(username):
    if not isinstance(username, str) or not username.strip():
        return False, "Username cannot be empty."
    username = username.strip()
    if not USERNAME_RE.match(username):
        return False, "Username must be 3-20 characters long and contain only letters, numbers, and underscores."
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    if exists:
        return False, "Username already taken. Please choose another."
    return True, None

def validate_password(password):
    if not isinstance(password, str):
        return False, "Password must be text."
    if not PASSWORD_RE.match(password):
        return False, ("Password must be 8-30 characters and include at least one uppercase letter, "
                       "one lowercase letter, one number, and one special character.")
    return True, None

def register_user(full_name, username, password, initial_deposit):
    ok, err = validate_full_name(full_name)
    if not ok:
        return False, err

    ok, err = validate_username(username)
    if not ok:
        return False, err

    ok, err = validate_password(password)
    if not ok:
        return False, err

    # initial_deposit numeric and >= 2000
    try:
        initial_deposit = float(initial_deposit)
    except (TypeError, ValueError):
        return False, "Initial deposit must be a number."

    if initial_deposit < 2000:
        return False, "Initial deposit must be at least ₦2,000."

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    account_number = _make_unique_account_number()

    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (full_name, username, password, account_number, balance)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name.strip(), username.strip(), hashed_pw, account_number, initial_deposit))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False, "Registration failed: username or account number already exists."
    finally:
        conn.close()

    time.sleep(0.6)
    return True, f"Account created successfully! Your account number is {account_number}"

def login_user(username, password):
    if not username or not password:
        return None, "Username and password are required."

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        return None, "No account found with that username."

    stored = row["password"]
    if isinstance(stored, str):
        stored = stored.encode("utf-8")
    try:
        if bcrypt.checkpw(password.encode("utf-8"), stored):
            time.sleep(0.3)
            # return row as tuple-like (id, full_name, username, ...)
            return row, None
        else:
            return None, "Incorrect password."
    except ValueError:
        return None, "Password verification failed due to invalid hash."
