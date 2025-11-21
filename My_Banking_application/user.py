# user.py
import sqlite3
import random
import re
import bcrypt
import time
from database import get_connection

# ----------------------------------------------------------
# Regular expressions for validating user input
# ----------------------------------------------------------

# Full name: alphabets + spaces, up to 3 words (first, middle, last)
FULLNAME_RE = re.compile(r"^[A-Za-z]+(?: [A-Za-z]+){1,2}$")

# Username: 3–20 characters, letters, numbers, underscores
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{4,20}$")

# Password: 8–30 characters, uppercase, lowercase, number, special
PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,30}$"
)


# ----------------------------------------------------------
# Account number generation helpers
# ----------------------------------------------------------
def generate_account_number():
    """Create a random 8-digit account number as a string."""
    return f"{random.randint(0, 99999999):08d}"


def is_account_number_unique(account_number):
    """Check if a generated account number already exists."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE account_number = ?",
        (account_number,)
    )

    exists = cursor.fetchone() is not None
    conn.close()

    return not exists


def make_unique_account_number():
    """Generate a new unique account number (retries if needed)."""
    for _ in range(50):
        number = generate_account_number()
        if is_account_number_unique(number):
            return number

    raise RuntimeError("Could not generate a unique account number.")


# ----------------------------------------------------------
# Validation functions
# ----------------------------------------------------------
def validate_full_name(name):
    """Require a full name that is 2 to 3 words (first + at least one more),
    only letters and spaces, and length between 4 and 255 characters."""
    if not isinstance(name, str):
        return False, "Full name must be text."

    name = name.strip()

    if not (4 <= len(name) <= 255):
        return False, "Full name must be between 4 and 255 characters."

    # Require 2 to 3 words containing only letters and single spaces between words
    if not FULLNAME_RE.match(name):
        return False, (
            "Full name must contain only letters and spaces, "
            "and include at least two names (first and last)."
        )

    return True, None



def validate_username(username):
    """Validate the username format and check if it's unique."""
    if not isinstance(username, str) or not username.strip():
        return False, "Username cannot be empty."

    username = username.strip()

    if not USERNAME_RE.match(username):
        return False, (
            "Username must be 4-20 characters and contain only letters, "
            "numbers, and underscores."
        )

    # Check if username already exists
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    exists = cursor.fetchone() is not None
    conn.close()

    if exists:
        return False, "Username already taken."

    return True, None


def validate_password(password):
    """Validate password strength."""
    if not isinstance(password, str):
        return False, "Password must be text."

    if not PASSWORD_RE.match(password):
        return False, (
            "Password must be 8–30 characters and include: "
            "• one uppercase letter\n"
            "• one lowercase letter\n"
            "• one number\n"
            "• one special character"
        )

    return True, None


# ----------------------------------------------------------
# Register (Create Account)
# ----------------------------------------------------------
def register_user(full_name, username, password, initial_deposit):
    """Create a new user account after validating all inputs."""

    # Validate full name
    ok, error = validate_full_name(full_name)
    if not ok:
        return False, error

    # Validate username
    ok, error = validate_username(username)
    if not ok:
        return False, error

    # Validate password
    ok, error = validate_password(password)
    if not ok:
        return False, error

    # Validate initial deposit
    try:
        initial_deposit = float(initial_deposit)
    except ValueError:
        return False, "Initial deposit must be a number."

    if initial_deposit < 2000:
        return False, "Initial deposit must be at least ₦2,000."

    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Generate unique account number
    account_number = make_unique_account_number()

    # Save user in database
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (full_name, username, password, account_number, balance)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name.strip(), username.strip(), hashed_pw, account_number, initial_deposit)
        )

        conn.commit()

    except sqlite3.IntegrityError:
        return False, "Registration failed: username or account number already exists."

    finally:
        conn.close()

    time.sleep(0.6)
    return True, f"Account created successfully! Your account number is {account_number}"


# ----------------------------------------------------------
# Login
# ----------------------------------------------------------
def login_user(username, password):
    """Authenticate a user by checking username + password."""

    if not username or not password:
        return None, "Username and password are required."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        return None, "No account found with that username. Please register an account"

    stored_hash = user_row["password"]

    # Stored hash might be bytes or string depending on DB
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    # Compare passwords
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        time.sleep(0.3)
        return user_row, None

    return None, "Incorrect password."
