import sqlite3

def create_database(cursor):
    # This is an example schema — Replace these with our SQL statements from Part 2
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY,
        name TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rewards (
        id INTEGER PRIMARY KEY,
        member_id INTEGER,
        month INTEGER,
        year INTEGER,
        amount REAL,
        FOREIGN KEY (member_id) REFERENCES members(id)
    );
    """)
    

def generate_rewards_notice(cursor):
    print("\nGenerating a rewards notice for a member...")
    member_id = int(input("Member ID number: "))
    month = int(input("Month: "))
    year = int(input("Year: "))

    cursor.execute("""
        SELECT members.name, rewards.amount
        FROM rewards
        JOIN members ON rewards.member_id = members.id
        WHERE rewards.member_id = ? AND rewards.month = ? AND rewards.year = ?;
    """, (member_id, month, year))

    result = cursor.fetchone()
    if result:
        name, amount = result
        print(f"\nRewards notice for member {name} during {month:02}/{year}: ${amount:.2f}")
    else:
        print("\nNo rewards found for that member and date.")

def command_line_ui(cursor):
    print("Welcome to MuskieCo.\n")
    print("Which task would you like to perform?")
    print("1. Information Processing")
    print("2. Inventory Records")
    print("3. Billing and Transaction Records")
    print("4. Reports")

    task_choice = input("Enter the number corresponding to your choice: ").strip()

    if task_choice == "3":
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
    else:
        print("Feature not implemented yet.")

def main():
    conn = sqlite3.connect(":memory:")  
    cursor = conn.cursor()

    create_database(cursor)

    
    cursor.execute("INSERT OR IGNORE INTO members (id, name) VALUES (1, 'Kara Schatz')")
    cursor.execute("INSERT INTO rewards (member_id, month, year, amount) VALUES (1, 4, 2025, 50)")
    conn.commit()

    # Start CLI
    command_line_ui(cursor)

    conn.close()

if __name__ == "__main__":
    main()
