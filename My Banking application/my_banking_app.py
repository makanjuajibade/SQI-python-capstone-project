import sqlite3
import random
import datetime

DB_FILE = "bankapp.db"

with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    account_number TEXT UNIQUE,
    password TEXT,
    balance REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number TEXT,
    type TEXT,
    amount REAL,
    date TEXT,
    details TEXT
)
""")

conn.commit()

# ====== BANK SYSTEM CLASS ======
class BankSystem:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def generate_account_number(self):
        return str(random.randint(1000000000, 9999999999))

    def create_account(self, name, password):
        account_number = self.generate_account_number()
        self.cursor.execute("INSERT INTO users (name, account_number, password, balance) VALUES (?, ?, ?, ?)",
                            (name, account_number, password, 0))
        self.conn.commit()
        print(f"✅ Account created successfully! Your account number is {account_number}")

    def login(self, account_number, password):
        self.cursor.execute("SELECT * FROM users WHERE account_number=? AND password=?", (account_number, password))
        user = self.cursor.fetchone()
        if user:
            print(f"Welcome back, {user[1]}!")
            return user
        else:
            print("❌ Invalid account number or password.")
            return None

    def deposit(self, account_number, amount):
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, account_number))
        self.cursor.execute("INSERT INTO transactions (account_number, type, amount, date, details) VALUES (?, ?, ?, ?, ?)",
                            (account_number, "Deposit", amount, datetime.datetime.now(), f"Deposited ₦{amount}"))
        self.conn.commit()
        print(f"✅ Successfully deposited ₦{amount}")

    def withdraw(self, account_number, amount):
        self.cursor.execute("SELECT balance FROM users WHERE account_number=?", (account_number,))
        balance = self.cursor.fetchone()[0]
        if balance >= amount:
            self.cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number=?", (amount, account_number))
            self.cursor.execute("INSERT INTO transactions (account_number, type, amount, date, details) VALUES (?, ?, ?, ?, ?)",
                                (account_number, "Withdrawal", amount, datetime.datetime.now(), f"Withdrew ₦{amount}"))
            self.conn.commit()
            print(f"✅ Successfully withdrew ₦{amount}")
        else:
            print("❌ Insufficient funds.")

    def transfer(self, sender_acc, receiver_acc, amount):
        # Check sender balance
        self.cursor.execute("SELECT balance FROM users WHERE account_number=?", (sender_acc,))
        sender_balance = self.cursor.fetchone()[0]

        if sender_balance >= amount:
            self.cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number=?", (amount, sender_acc))
            self.cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number=?", (amount, receiver_acc))
            self.cursor.execute("INSERT INTO transactions (account_number, type, amount, date, details) VALUES (?, ?, ?, ?, ?)",
                                (sender_acc, "Transfer", amount, datetime.datetime.now(), f"Transferred to {receiver_acc}"))
            self.cursor.execute("INSERT INTO transactions (account_number, type, amount, date, details) VALUES (?, ?, ?, ?, ?)",
                                (receiver_acc, "Received", amount, datetime.datetime.now(), f"Received from {sender_acc}"))
            self.conn.commit()
            print("✅ Transfer successful!")
        else:
            print("❌ Insufficient balance.")

    def check_balance(self, account_number):
        self.cursor.execute("SELECT balance FROM users WHERE account_number=?", (account_number,))
        balance = self.cursor.fetchone()[0]
        print(f"💰 Your current balance is ₦{balance}")

    def transaction_history(self, account_number):
        self.cursor.execute("SELECT * FROM transactions WHERE account_number=? ORDER BY date DESC", (account_number,))
        transactions = self.cursor.fetchall()
        if transactions:
            print("\n📜 Transaction History:")
            for t in transactions:
                print(f"{t[4]} | {t[2]} ₦{t[3]} | {t[5]}")
        else:
            print("No transactions yet.")

