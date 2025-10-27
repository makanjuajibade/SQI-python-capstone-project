import sqlite3
import random
from database import get_connection

def generate_account_number():
    return "05" + str(random.randint(10000000, 99999999))

def register_user(full_name, username, password, initial_deposit):
    conn = get_connection()
    cursor = conn.cursor()
    account_number = generate_account_number()

    try:
        cursor.execute("""
            INSERT INTO users (full_name, username, password, account_number, balance)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, username, password, account_number, initial_deposit))
        conn.commit()
        print(f"\n Account created successfully! Your account number is {account_number}")
    except sqlite3.IntegrityError:
        print("\n Username already exists. Try another one.")
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user
