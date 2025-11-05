# banking.py
import time
from database import get_connection
from user import validate_full_name

def log_transaction(user_id, t_type, amount, counterparty=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO transactions (user_id, type, amount, counterparty) VALUES (?, ?, ?, ?)",
        (user_id, t_type, amount, counterparty)
    )
    conn.commit()
    conn.close()

def check_balance(user_row):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id = ?", (user_row["id"],))
    balance = c.fetchone()[0]
    conn.close()
    time.sleep(0.25)  
    print(f"\n💰 Current balance: ₦{balance:,.2f}")
    return balance

def deposit(user_row, amount):
    # validate amount numeric positive
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False, "Deposit amount must be a number."

    if amount <= 0:
        return False, "Deposit amount must be a positive number."

    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_row["id"]))
    conn.commit()
    conn.close()
    log_transaction(user_row["id"], "Deposit", amount)
    time.sleep(0.4)
    return True, f"Deposit of ₦{amount:,.2f} successful."

def withdraw(user_row, amount):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False, "Withdrawal amount must be a number."

    if amount <= 0:
        return False, "Withdrawal amount must be a positive number."

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id = ?", (user_row["id"],))
    current = c.fetchone()[0]

    if amount > current:
        conn.close()
        return False, "Insufficient funds."
    c.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user_row["id"]))
    conn.commit()
    conn.close()
    log_transaction(user_row["id"], "Withdrawal", amount)
    time.sleep(0.4)
    return True, f"Withdrawal of ₦{amount:,.2f} successful."

def _find_user_by_account(account_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE account_number = ?", (account_number,))
    row = c.fetchone()
    conn.close()
    return row

def transfer(user_row, target_account_number, amount):
    # cannot transfer to self
    if target_account_number == user_row["account_number"]:
        return False, "You cannot transfer to your own account."

    # amount validation
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False, "Transfer amount must be a number."

    if amount <= 0:
        return False, "Transfer amount must be a positive number."

    # find target user
    target = _find_user_by_account(target_account_number)
    if not target:
        return False, "Target account not found."

    # check balance
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id = ?", (user_row["id"],))
    sender_balance = c.fetchone()[0]
    if amount > sender_balance:
        conn.close()
        return False, "Insufficient funds for this transfer."

    # perform transfer inside transaction
    try:
        c.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user_row["id"]))
        c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, target["id"]))
        # log both sides
        c.execute("INSERT INTO transactions (user_id, type, amount, counterparty) VALUES (?, ?, ?, ?)",
                  (user_row["id"], "Transfer Out", amount, target["account_number"]))
        c.execute("INSERT INTO transactions (user_id, type, amount, counterparty) VALUES (?, ?, ?, ?)",
                  (target["id"], "Transfer In", amount, user_row["account_number"]))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return False, "Transfer failed due to a database error."
    finally:
        conn.close()

    time.sleep(0.6)
    return True, f"Transfer of ₦{amount:,.2f} to {target['full_name']} ({target['account_number']}) successful."

def view_transactions(user_row, limit=50):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT type, amount, counterparty, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_row["id"], limit)
    )
    rows = c.fetchall()
    conn.close()
    time.sleep(0.25)

    if not rows:
        print("\nThere are no transactions yet.")
        return

    print("\n===== TRANSACTION HISTORY =====")
    print(f"{'Date':19} | {'Type':12} | {'Amount':15} | {'Counterparty'}")
    print("-" * 70)
    for r in rows:
        ts = r["timestamp"]
        ttype = r["type"]
        amt = f"₦{r['amount']:,.2f}"
        cp = r["counterparty"] if r["counterparty"] else "-"
        print(f"{ts:19} | {ttype:12} | {amt:15} | {cp}")
