from database import get_connection

def log_transaction(user_id, type, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (user_id, type, amount) VALUES (?, ?, ?)",
        (user_id, type, amount)
    )
    conn.commit()
    conn.close()

def check_balance(user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id=?", (user[0],))
    balance = cursor.fetchone()[0]
    conn.close()
    print(f"\nYour current balance is: ₦{balance:.2f}")

def deposit(user, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user[0]))
    conn.commit()
    conn.close()
    log_transaction(user[0], "Deposit", amount)
    print(f"\nDeposit of ₦{amount:.2f} successful!")

def withdraw(user, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id=?", (user[0],))
    balance = cursor.fetchone()[0]
    
    if amount > balance:
        print("\nInsufficient funds.")
    else:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, user[0]))
        conn.commit()
        conn.close()
        log_transaction(user[0], "Withdrawal", amount)
        print(f"\nWithdrawal of ₦{amount:.2f} successful!")

def view_transactions(user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT type, amount, timestamp FROM transactions WHERE user_id=? ORDER BY timestamp DESC",
        (user[0],)
    )
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("\nNo transactions found.")
    else:
        print("\n===== TRANSACTION HISTORY =====")
        for t_type, amount, time in records:
            print(f"{time} | {t_type:<10} | ₦{amount:.2f}")
