# banking.py
import time
from database import get_connection


# ----------------------------------------------------------
# Helper function to log transactions
# ----------------------------------------------------------
def log_transaction(user_id, t_type, amount, counterparty=None):
    """Save a transaction record for a user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO transactions (user_id, type, amount, counterparty)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, t_type, amount, counterparty)
    )

    conn.commit()
    conn.close()


# ----------------------------------------------------------
# Check current balance
# ----------------------------------------------------------
def check_balance(user_row):
    """Return and display the current balance for a user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_row["id"],))
    balance = cursor.fetchone()[0]

    conn.close()

    time.sleep(0.25)
    print(f"\n💰 Current balance: ₦{balance:,.2f}")
    return balance


# ----------------------------------------------------------
# Deposit money
# ----------------------------------------------------------
def deposit(user_row, amount):
    """Deposit money into the user's account."""
    
    # Convert amount to number
    try:
        amount = float(amount)
    except ValueError:
        return False, "Deposit amount must be a number."

    # Must be positive
    if amount <= 0:
        return False, "Amount must be greater than zero."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE id = ?",
        (amount, user_row["id"])
    )

    conn.commit()
    conn.close()

    log_transaction(user_row["id"], "Deposit", amount)
    time.sleep(0.4)

    return True, f"Deposit of ₦{amount:,.2f} successful."


# ----------------------------------------------------------
# Withdraw money
# ----------------------------------------------------------
def withdraw(user_row, amount):
    """Withdraw money from a user's account."""

    try:
        amount = float(amount)
    except ValueError:
        return False, "Withdrawal amount must be a number."

    if amount <= 0:
        return False, "Amount must be greater than zero."

    conn = get_connection()
    cursor = conn.cursor()

    # Check current balance
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_row["id"],))
    current_balance = cursor.fetchone()[0]

    if amount > current_balance:
        conn.close()
        return False, "Insufficient funds."

    # Deduct money
    cursor.execute(
        "UPDATE users SET balance = balance - ? WHERE id = ?",
        (amount, user_row["id"])
    )

    conn.commit()
    conn.close()

    log_transaction(user_row["id"], "Withdrawal", amount)
    time.sleep(0.4)

    return True, f"Withdrawal of ₦{amount:,.2f} successful."


# ----------------------------------------------------------
# Find user by account number (used for transfers)
# ----------------------------------------------------------
def find_user_by_account(account_number):
    """Return the user row belonging to a given account number."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE account_number = ?",
        (account_number,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


# ----------------------------------------------------------
# Transfer money
# ----------------------------------------------------------
def transfer(user_row, target_account_number, amount):
    """Send money from one user to another."""

    # Cannot transfer to yourself
    if target_account_number == user_row["account_number"]:
        return False, "You cannot transfer to your own account."

    # Convert amount
    try:
        amount = float(amount)
    except ValueError:
        return False, "Amount must be a number."

    if amount <= 0:
        return False, "Amount must be greater than zero."

    # Get target user
    target_user = find_user_by_account(target_account_number)
    if not target_user:
        return False, "Target account not found."

    conn = get_connection()
    cursor = conn.cursor()

    # Check sender balance
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_row["id"],))
    sender_balance = cursor.fetchone()[0]

    if amount > sender_balance:
        conn.close()
        return False, "Insufficient funds."

    # Perform the transfer
    try:
        # Deduct from sender
        cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE id = ?",
            (amount, user_row["id"])
        )

        # Add to receiver
        cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE id = ?",
            (amount, target_user["id"])
        )

        # Log transactions
        log_transaction(user_row["id"], "Transfer Out", amount, target_user["account_number"])
        log_transaction(target_user["id"], "Transfer In", amount, user_row["account_number"])

        conn.commit()

    except Exception:
        conn.rollback()
        conn.close()
        return False, "Transfer failed due to a database error."

    conn.close()
    time.sleep(0.6)

    return True, f"Transfer of ₦{amount:,.2f} to {target_user['full_name']} successful."


# ----------------------------------------------------------
# View transaction history
# ----------------------------------------------------------
def view_transactions(user_row, limit=50):
    """Print a user's transaction history."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT type, amount, counterparty, timestamp
        FROM transactions
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (user_row["id"], limit)
    )

    transactions = cursor.fetchall()
    conn.close()
    time.sleep(0.25)

    if not transactions:
        print("\nNo transactions yet.")
        return

    print("\n===== TRANSACTION HISTORY =====")
    print(f"{'Date':19} | {'Type':12} | {'Amount':15} | {'Counterparty'}")
    print("-" * 70)

    for row in transactions:
        date = row["timestamp"]
        t_type = row["type"]
        amount_str = f"₦{row['amount']:,.2f}"
        cp = row["counterparty"] if row["counterparty"] else "-"

        print(f"{date:19} | {t_type:12} | {amount_str:15} | {cp}")
