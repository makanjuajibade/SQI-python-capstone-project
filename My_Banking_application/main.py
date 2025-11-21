# main.py

import getpass
import time

from database import create_tables, get_connection
from user import register_user, login_user
from my_banking_app import (
    check_balance, deposit, withdraw,
    transfer, view_transactions
)


# ---------------------------------------------
# SIMPLE PASSWORD INPUT
# ---------------------------------------------
def prompt_password():
    return getpass.getpass("Password: ")


# ---------------------------------------------
# LOAD USER DATA AGAIN AFTER BALANCE CHANGES
# ---------------------------------------------
def refresh_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


# ---------------------------------------------
# MAIN MENU FOR ALL USERS
# ---------------------------------------------
def show_main_menu():
    print("\n===== WELCOME TO SQI BANK =====")
    print("1. Register")
    print("2. Login")
    print("3. Exit")


# ---------------------------------------------
# MENU FOR LOGGED-IN USERS
# ---------------------------------------------
def show_user_menu():
    print("\n===== ACCOUNT MENU =====")
    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Transfer")
    print("5. View Transactions")
    print("6. Logout")


# ---------------------------------------------
# MAIN PROGRAM LOOP
# ---------------------------------------------
def main():
    create_tables()  # ensure tables exist
    current_user = None

    while True:

        # If no user is logged in → Show main menu
        if current_user is None:
            show_main_menu()
            choice = input("Enter choice: ").strip()

            if choice == "1":
                full_name = input("Full name: ").strip()
                username = input("Username: ").strip()
                password = prompt_password()
                initial = input("Initial deposit (₦): ").strip()

                success, msg = register_user(full_name, username, password, initial)
                print(msg)

            elif choice == "2":
                username = input("Username: ").strip()
                password = prompt_password()

                user_row, msg = login_user(username, password)

                if user_row:
                    current_user = user_row
                    print(f"\nWelcome, {current_user['full_name']}!")
                else:
                    print(msg)

            elif choice == "3":
                print(f"Goodbye, {current_user['full_name']}.")
                break

            else:
                print("Invalid option. Try again.")

        # If a user is logged in → Show user menu
        else:
            show_user_menu()
            choice = input("Enter choice: ").strip()

            if choice == "1":
                check_balance(current_user)

            elif choice == "2":
                amount = input("Amount to deposit (₦): ")
                ok, msg = deposit(current_user, amount)
                print(msg)
                current_user = refresh_user(current_user["username"])

            elif choice == "3":
                amount = input("Amount to withdraw (₦): ")
                ok, msg = withdraw(current_user, amount)
                print(msg)
                current_user = refresh_user(current_user["username"])

            elif choice == "4":
                target = input("Target account number: ")
                amount = input("Amount to transfer (₦): ")
                ok, msg = transfer(current_user, target, amount)
                print(msg)
                current_user = refresh_user(current_user["username"])

            elif choice == "5":
                view_transactions(current_user)

            elif choice == "6":
                print("Logging out...")
                time.sleep(0.5)
                current_user = None

            else:
                print("Invalid option. Try again.")


# ---------------------------------------------
# START PROGRAM
# ---------------------------------------------
if __name__ == "__main__":
    main()
