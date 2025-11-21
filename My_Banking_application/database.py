# database.py
import sqlite3

# Path to the SQLite database file
DB_PATH = "bank.db"

def get_connection():
    """Create and return a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Makes rows behave like dictionaries
    return conn

def create_tables():
    """Create the required tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table stores each user's account info
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0
        )
    """)

    # Transactions table stores all deposits, withdrawals, transfers, etc.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            counterparty TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()
