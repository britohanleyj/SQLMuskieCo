import mysql.connector
import getpass

from apis import (
    enter_store, search_store, update_store, delete_store,
    enter_member, search_member, update_member, delete_member,
    enter_staff, search_staff, update_staff, delete_staff,
    enter_discount, search_discount, update_discount, delete_discount,
    update_inventory
)

def generate_rewards_notice(cursor):
    print("\nGenerating a rewards notice for a member...")
    member_id = int(input("Member ID number: "))
    month = int(input("Month: "))
    year = int(input("Year: "))

    cursor.execute("""
        SELECT members.name, rewards.amount
        FROM rewards
        JOIN members ON rewards.member_id = members.id
        WHERE rewards.member_id = %s AND rewards.month = %s AND rewards.year = %s;
    """, (member_id, month, year))

    result = cursor.fetchone()
    if result:
        name, amount = result
        print(f"\nRewards notice for member {name} during {month:02}/{year}: ${amount:.2f}")
    else:
        print("\nNo rewards found for that member and date.")


def command_line_ui(cursor):
    print("Welcome to MuskieCo.\n")

    while True:
        print("\nMain Menu — What would you like to do?")
        print("1. Information Processing")
        print("2. Update Inventory Records")
        print("3. Billing and Transaction Records")
        print("4. Reports")
        print("5. Exit")

        task_choice = input("Enter the number corresponding to your choice: ").strip()

        if task_choice == "1":
            print("\nWhich Information Processing operation would you like to perform?")
            print("1. Store Info")
            print("2. Member Info")
            print("3. Staff Info")
            print("4. Discount Info")
            info_choice = input("Choose a category: ").strip()

            def handle_ops(enter, search, update, delete):
                print("\nChoose an operation:")
                print("1. Enter")
                print("2. Search")
                print("3. Update")
                print("4. Delete")
                op = input("Operation: ").strip()
                if op == "1":
                    enter(cursor)
                elif op == "2":
                    search(cursor)
                elif op == "3":
                    update(cursor)
                elif op == "4":
                    delete(cursor)
                else:
                    print("Invalid choice.")

            if info_choice == "1":
                handle_ops(enter_store, search_store, update_store, delete_store)
            elif info_choice == "2":
                handle_ops(enter_member, search_member, update_member, delete_member)
            elif info_choice == "3":
                handle_ops(enter_staff, search_staff, update_staff, delete_staff)
            elif info_choice == "4":
                handle_ops(enter_discount, search_discount, update_discount, delete_discount)
            else:
                print("Invalid category.")

        elif task_choice == "2":
            update_inventory(cursor)

        elif task_choice == "3":
            print("\nWhich billing and transaction operation would you like to perform?")
            print("1. Generate reward notices for members")
            print("2. Generate rewards checks for employees")
            print("3. Calculate the total price of a transaction")
            operation = input("Enter the number corresponding to your choice: ").strip()

            if operation == "1":
                generate_rewards_notice(cursor)
            elif operation == "2":
                print("Feature not implemented yet.")
            elif operation == "3":
                print("Feature not implemented yet.")
            else:
                print("Invalid choice.")

        elif task_choice == "4":
            print("Reports feature not implemented yet.")

        elif task_choice == "5":
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid selection. Please try again.")


def main():
    print("MySQL Database Login\n")
    user = input("Enter MySQL username: ")
    password = getpass.getpass("Enter MySQL password: ")

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user=user,
            password=password,
            database="muskieco"
        )
        cursor = connection.cursor()
        command_line_ui(cursor)
        connection.commit()
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Failed to connect: {err}")


if __name__ == "__main__":
    main()
