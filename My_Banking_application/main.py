
from database import create_tables
from user import register_user, login_user
from my_banking_app import check_balance, deposit, withdraw, view_transactions

def main():
    create_tables()

    while True:
        print("\n===== WELCOME TO KAY BANK =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            full_name = input("Full name: ")
            username = input("Username: ")
            password = input("Password: ")
            initial_deposit = float(input("Initial deposit: ₦"))
            register_user(full_name, username, password, initial_deposit)

        elif choice == "2":
            username = input("Username: ")
            password = input("Password: ")
            user = login_user(username, password)

            if user:
                print(f"\nWelcome, {user[1]}!")
                while True:
                    print("\n1. Check Balance\n2. Deposit\n3. Withdraw\n4. View Transactions\n5. Logout")
                    op = input("Choose operation: ")

                    if op == "1":
                        check_balance(user)
                    elif op == "2":
                        amount = float(input("Enter amount to deposit: ₦"))
                        deposit(user, amount)
                    elif op == "3":
                        amount = float(input("Enter amount to withdraw: ₦"))
                        withdraw(user, amount)
                    elif op == "4":
                        view_transactions(user)
                    elif op == "5":
                        print("Logging out...\n")
                        break
                    else:
                        print("Invalid option.")
            else:
                print("\n❌ Invalid username or password.")

        elif choice == "3":
            print("Thank you for using SQI Bank!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
