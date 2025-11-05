# main.py
import getpass
import time
from database import create_tables
from user import register_user, login_user
from my_banking_app import check_balance, deposit, withdraw, view_transactions, transfer

def prompt_password(mask=True):
    # getpass masks input on terminal
    return getpass.getpass("Password: ")

def main_menu():
    create_tables()
    current_user = None  # store sqlite Row when logged in

    while True:
        print("\n===== WELCOME TO SQI BANK =====")
        print("1. Register")
        print("2. Login")
        if current_user:
            print("3. Check Balance")
            print("4. Deposit")
            print("5. Withdraw")
            print("6. Transfer")
            print("7. View Transactions")
            print("8. Logout")
            print("9. Exit")
        else:
            print("3. Exit")

        choice = input("Enter choice: ").strip()

        if not current_user:
            if choice == "1":
                full_name = input("Full name: ").strip()
                username = input("Username: ").strip()
                password = prompt_password()
                initial_deposit = input("Initial deposit (₦): ").strip()
                success, msg = register_user(full_name, username, password, initial_deposit)
                print(msg)
            elif choice == "2":
                username = input("Username: ").strip()
                password = prompt_password()
                user_row, err = login_user(username, password)
                if user_row:
                    current_user = user_row
                    print(f"\nWelcome, {current_user['full_name']}!")
                else:
                    print(f"\n{err}")
            elif choice == "3":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")
        else:
            if choice == "3":
                check_balance(current_user)
            elif choice == "4":
                amount = input("Amount to deposit (₦): ").strip()
                ok, msg = deposit(current_user, amount)
                print(msg)
                # refresh user data
                current_user = _refresh_user(current_user["username"])
            elif choice == "5":
                amount = input("Amount to withdraw (₦): ").strip()
                ok, msg = withdraw(current_user, amount)
                print(msg)
                current_user = _refresh_user(current_user["username"])
            elif choice == "6":
                target = input("Target account number: ").strip()
                amount = input("Amount to transfer (₦): ").strip()
                ok, msg = transfer(current_user, target, amount)
                print(msg)
                current_user = _refresh_user(current_user["username"])
            elif choice == "7":
                view_transactions(current_user)
            elif choice == "8":
                print("Logging out...")
                time.sleep(0.4)
                current_user = None
            elif choice == "9":
                print("Thank you for using SQI Bank. Goodbye.")
                break
            else:
                print("Invalid choice.")

def _refresh_user(username):
    # helper to reload fresh user data from DB after balance changes
    from database import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row

if __name__ == "__main__":
    main_menu()
