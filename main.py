'''
Authors: Carter Lange, Julian-Brito Hanley, Lance Silliman, Evan Gunnulfusen

The purpose of this file is to provide a command line interface (CLI) to interact with the MuskieCo database system

This file:
    1. Connects to a MySQL database using user credentials
    2. Delegates database operations
    3. Supports inventory updates and basic reporting features
'''

import mysql.connector
import getpass

from apis import (
    enter_store, search_store, update_store, delete_store,
    enter_member, search_member, update_member, delete_member,
    enter_staff, search_staff, update_staff, delete_staff,
    enter_discount, search_discount, update_discount, delete_discount,
    update_inventory, generate_report, view_customer_rewards,
    reset_customer_rewards, view_staff_signups, reset_staff_signups,
    view_product_prices, view_final_prices
)



def command_line_ui(cursor):
    
    '''
    This function displays the command-line interface for MuskieCo system and handles user interaction
    
    Parameters:
        cursor - A cursor object that is used to execute MySQL queries
    
    Returns:
        None
    '''
    
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
                '''
                This handles operations for a given entity type
                
                Parameters:
                    enter(function): Function to enter a new record
                    search(function): Function to search for a record
                    update(function): Function to update a record
                    delete(function): Function to delete a record
                    
                Returns:
                    None
                '''
                
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
            print("4. Reset customer rewards")
            print("5. Reset signups staff obtained.")
            print("6. Generate final prices.")
            operation = input("Enter the number corresponding to your choice: ").strip()

            if operation == "1":
                view_customer_rewards(cursor)
            elif operation == "2":
                view_staff_signups(cursor)
            elif operation == "3":
                view_product_prices(cursor)
            elif operation == "4":
                reset_customer_rewards(cursor)
            elif operation == "5":
                reset_staff_signups(cursor)
            elif operation == "6":
                view_final_prices(cursor)
            else:
                print("Invalid choice.")

        elif task_choice == "4":
            generate_report(cursor)

        elif task_choice == "5":
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid selection. Please try again.")


def main():
    '''
    Main function of the MuskieCo CLI system
    
    Prompts for MySQL login credentials, establishes a connection, and launches the command-line UI
    
    Returns:
        None
    '''
    
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
