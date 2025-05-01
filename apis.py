'''
Authors: Carter Lange, Julian-Brito Hanley, Lance Silliman, Evan Gunnulfusen

The purpose of this file is to serve as a backend administrative interface for MuskieCo.

It allows DBA's to:
    1. Manually manage and maintain
        - staff
        - discount
        - inventory

'''

import mysql.connector

# ------ Start of information processing ------

# ------ Store info ------

def enter_store(cursor):
    '''
    Inserts a new store into the database with address and phone number
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns:
        None
    '''
    
    store_addr = input("Enter store address: ").strip()
    phone = input("Enter store phone #: ").strip()

    try:
        # (i) START TRANSACTION — begins the atomic block of operations
        cursor.execute("START TRANSACTION")

        # Insert into StoreAddress (can fail due to unique constraint or bad input)
        cursor.execute(
            "INSERT INTO StoreAddress (StoreAddr, Phone) VALUES (%s, %s)",
            (store_addr, phone)
        )

        # Insert into Store (references the above StoreAddr)
        cursor.execute(
            "INSERT INTO Store (StoreAddr) VALUES (%s)",
            (store_addr,)
        )

        # (iii) COMMIT — both operations succeeded, so we save the changes permanently
        cursor.execute("COMMIT")
        print("Store added successfully.")

        # Show the inserted record
        cursor.execute("""
            SELECT Store.StoreID, Store.StoreAddr, StoreAddress.Phone
            FROM Store
            JOIN StoreAddress ON Store.StoreAddr = StoreAddress.StoreAddr
            WHERE Store.StoreAddr = %s
            ORDER BY StoreID DESC LIMIT 1
        """, (store_addr,))
        result = cursor.fetchone()
        print("New Store Record:", result)

    except mysql.connector.Error as e:
        # (ii) ROLLBACK — if any error occurred, undo all changes from this transaction
        cursor.execute("ROLLBACK")
        print("Error occurred, transaction rolled back.")
        print(f"MySQL Error: {e}")




def search_store(cursor):
    '''
    Searches for store(s) by StoreID or Store Address
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns: 
        None
    '''
    
    store_id = input("Enter Store ID (or press Enter to skip): ").strip()
    store_addr = input("Enter Store Address (or press Enter to skip): ").strip()

    query = """SELECT Store.StoreID, Store.StoreAddr, StoreAddress.Phone 
               FROM Store JOIN StoreAddress ON Store.StoreAddr = StoreAddress.StoreAddr WHERE 1=1"""
    params = []
    if store_id:
        query += " AND Store.StoreID = %s"
        params.append(store_id)
    if store_addr:
        query += " AND Store.StoreAddr = %s"
        params.append(store_addr)

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    if results:
        for row in results:
            print(f"StoreID: {row[0]}, Address: {row[1]}, Phone: {row[2]}")
    else:
        print("No store found.")


def update_store(cursor):
    '''
    This function updates store address and/or phone number based on StoreID
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns:
        None
    '''
    
    store_id = input("Enter the Store ID to update: ").strip()

    cursor.execute("SELECT StoreAddr FROM Store WHERE StoreID = %s", (store_id,))
    result = cursor.fetchone()

    if not result:
        print("No store found with that ID.")
        return

    current_addr = result[0]
    print(f"Current address: {current_addr}")

    new_addr = input("Enter new store address (or press Enter to keep current): ").strip()
    new_phone = input("Enter new phone number (or press Enter to keep current): ").strip()

    try:
        address_changed = new_addr and new_addr != current_addr
        phone_changed = bool(new_phone)

        if address_changed:
            cursor.execute("SELECT 1 FROM StoreAddress WHERE StoreAddr = %s", (new_addr,))
            if cursor.fetchone():
                print("That address already exists. Please update the phone separately if needed.")
                return

            if not phone_changed:
                cursor.execute("SELECT Phone FROM StoreAddress WHERE StoreAddr = %s", (current_addr,))
                phone_row = cursor.fetchone()
                new_phone = phone_row[0] if phone_row else "000-000-0000"

            cursor.execute("INSERT INTO StoreAddress (StoreAddr, Phone) VALUES (%s, %s)", (new_addr, new_phone))
            cursor.execute("UPDATE Store SET StoreAddr = %s WHERE StoreID = %s", (new_addr, store_id))
            print("Store address updated.")

            cursor.execute("SELECT COUNT(*) FROM Store WHERE StoreAddr = %s", (current_addr,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM StoreAddress WHERE StoreAddr = %s", (current_addr,))
                print("Old address deleted (no longer used).")

        elif phone_changed:
            cursor.execute("UPDATE StoreAddress SET Phone = %s WHERE StoreAddr = %s", (new_phone, current_addr))
            print("Phone number updated.")
        else:
            print("No changes made.")
            return

        # ✅ Show the updated row
        cursor.execute("""
            SELECT Store.StoreID, Store.StoreAddr, StoreAddress.Phone
            FROM Store
            JOIN StoreAddress ON Store.StoreAddr = StoreAddress.StoreAddr
            WHERE Store.StoreID = %s
        """, (store_id,))
        updated = cursor.fetchone()
        print("Updated Store Record:", updated)

    except mysql.connector.Error as e:
        print(f"Update failed: {e}")



def delete_store(cursor):
    '''
    This function deletes a store and its address using the StoreID
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns:
        None
        
    '''
    
    store_id = input("Enter Store ID to delete: ").strip()

    try:
        cursor.execute("SELECT StoreAddr FROM Store WHERE StoreID = %s", (store_id,))
        result = cursor.fetchone()

        if not result:
            print("No store found with that ID.")
            return

        store_addr = result[0]

        cursor.execute("DELETE FROM Store WHERE StoreID = %s", (store_id,))
        cursor.execute("DELETE FROM StoreAddress WHERE StoreAddr = %s", (store_addr,))
        print("Store and its address deleted successfully.")
    except mysql.connector.Error as e:
        print(f"Error deleting store: {e}")


# ------ Member info ------

def enter_member(cursor):
    '''
    This function inserts a new member with contact and account details
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns:
        None
        
    '''
    
    customer_id = int(input("CustomerID: "))
    email = input("Email: ")
    home_addr = input("Home Address: ")
    active = input("Active? (yes/no): ").lower() == "yes"
    reward_points = int(input("Rewards Points: "))
    staff_id = int(input("Staff ID sending notice: "))

    try:
        cursor.execute("INSERT INTO CustomerEmail (Email, CustomerName, HomeAddr, ActivateStatus, StaffIDSendsNotice, RewardPoints) VALUES (%s, %s, %s, %s, %s, %s)",
                       (email, email.split("@")[0], home_addr, active, staff_id, reward_points))
        cursor.execute("INSERT INTO MemberInfo (CustomerID, Email) VALUES (%s, %s)", (customer_id, email))
        print("Member entered successfully.")

        # Show the new member record
        cursor.execute("""
            SELECT CustomerID, Email, HomeAddr, ActivateStatus, StaffIDSendsNotice, RewardPoints
            FROM CustomerEmail JOIN MemberInfo USING(Email)
            WHERE CustomerID = %s
        """, (customer_id,))
        print("New Member Record:", cursor.fetchone())

    except mysql.connector.Error as e:
        print("Error entering member:", e)



def search_member(cursor):
    '''
    This function searches for a member using CustomerID or Email
    
    Parameters:
        cursor - Active MySQL cursor
    
    Returns:
        None
        
    '''
    query = """SELECT CustomerID, Email, HomeAddr, ActivateStatus, StaffIDSendsNotice, RewardPoints 
               FROM CustomerEmail JOIN MemberInfo USING(Email)"""
    param = input("Enter CustomerID or Email: ").strip()
    if param.isdigit():
        cursor.execute(query + " WHERE CustomerID = %s", (int(param),))
    else:
        cursor.execute(query + " WHERE Email = %s", (param,))
    result = cursor.fetchone()
    print("Member Info:", result if result else "No member found.")


def update_member(cursor):
    '''
    This function updates member details using address, status, rewards, and staffID
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns:
        None
    '''
    customer_id = int(input("CustomerID to update: "))

    cursor.execute("SELECT Email FROM MemberInfo WHERE CustomerID = %s", (customer_id,))
    result = cursor.fetchone()

    if not result:
        print("No member found with that CustomerID.")
        return

    email = result[0]
    home_addr = input("New Home Address: ")
    active = input("Active? (yes/no): ").lower() == "yes"
    reward_points = int(input("New Rewards Points: "))
    staff_id = int(input("New Staff ID sending notice: "))

    try:
        cursor.execute("""UPDATE CustomerEmail 
                          SET HomeAddr = %s, ActivateStatus = %s, StaffIDSendsNotice = %s, RewardPoints = %s
                          WHERE Email = %s""", (home_addr, active, staff_id, reward_points, email))
        cursor.execute("""SELECT CustomerID, Email, HomeAddr, ActivateStatus, StaffIDSendsNotice, RewardPoints
                          FROM CustomerEmail JOIN MemberInfo USING(Email)
                          WHERE Email = %s""", (email,))
        print("Updated Member Record:", cursor.fetchone())

    except mysql.connector.Error as e:
        print(f"Update failed: {e}")


def delete_member(cursor):
    '''
    Deletes a member record based on CustomerID or Email
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns:
        None
    '''
    param = input("Enter CustomerID or Email to delete: ").strip()
    try:
        if param.isdigit():
            cursor.execute("DELETE FROM MemberInfo WHERE CustomerID = %s", (int(param),))
        else:
            cursor.execute("DELETE FROM MemberInfo WHERE Email = %s", (param,))
            cursor.execute("DELETE FROM CustomerEmail WHERE Email = %s", (param,))
        print("Member deleted.")
    except mysql.connector.Error as e:
        print("Delete failed:", e)


# ------ Staff info ------

def enter_staff(cursor):
    '''
    Inserts a new staff member's details into the StaffEmails and StaffInfo tables
    
    Prompts the user for:
    - StaffID
    - Name, Age, Home Address
    - Job Title, Email
    - Date of Employment
    - Number of Sign-ups
    
    Returns:
        None
    '''
    
    staff_id = int(input("Staff ID Has Store: "))
    name = input("Name: ")
    age = int(input("Age: "))
    addr = input("Home Address: ")
    job = input("Job Title: ")
    email = input("Email: ")
    date = input("Time of Employment (YYYY-MM-DD): ")
    signups = int(input("# of Sign-Ups: "))

    try:
        cursor.execute("""INSERT INTO StaffEmails (StaffIDHasStore, StaffName, Age, HomeAddr, 
                          JobTitle, Email, TimeOfEmployment, NumberOfSignUps) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                       (staff_id, name, age, addr, job, email, date, signups))
        cursor.execute("INSERT INTO StaffInfo (StaffID, Email) VALUES (%s, %s)", (staff_id, email))
        print("Staff entered.")
    except mysql.connector.Error as e:
        print("Insert failed:", e)


def search_staff(cursor):
    '''
    Searches for a staff member by StaffID or Email
    
    Joins StaffEmails and StaffInfo on Email to retrieve staff details
    Displays the staff information if found, otherwise indicates no match
    
    '''
    param = input("Enter StaffID or Email: ").strip()
    query = """SELECT StaffID, StaffIDHasStore, StaffName, Age, HomeAddr, 
               JobTitle, Email, TimeOfEmployment, NumberOfSignUps 
               FROM StaffEmails JOIN StaffInfo USING(Email)"""

    if param.isdigit():
        cursor.execute(query + " WHERE StaffID = %s", (int(param),))
    else:
        cursor.execute(query + " WHERE Email = %s", (param,))
    result = cursor.fetchone()
    print("Staff info:", result if result else "No match.")


def update_staff(cursor):
    '''
    Updates the details of an existing staff member in the StaffEmails table
    
    User Inputs:
    - Updated StaffIDHasStore, Name, Age, Home Address, Job Title, Employment Date, Number of Signups
    - Email
    
    Runs a SQL UPDATE statement using the email address
    
    '''
    staff_id = int(input("Staff ID Has Store: "))
    name = input("New Name: ")
    age = int(input("New Age: "))
    addr = input("New Home Address: ")
    job = input("New Job Title: ")
    email = input("Email: ")
    date = input("Time of Employment (YYYY-MM-DD): ")
    signups = int(input("New # of Sign-Ups: "))

    try:
        cursor.execute("""UPDATE StaffEmails 
                          SET StaffIDHasStore=%s, StaffName=%s, Age=%s, HomeAddr=%s, 
                          JobTitle=%s, TimeOfEmployment=%s, NumberOfSignUps=%s 
                          WHERE Email=%s""",
                       (staff_id, name, age, addr, job, date, signups, email))
        print("Staff updated.")
    except mysql.connector.Error as e:
        print("Update failed:", e)


def delete_staff(cursor):
    '''
    Deletes a staff member from StaffInfo and optionally StaffEmails
    
    Accepts either StaffID or Email
    - If StaffID is provided, deletes from StaffInfo only
    - If Email is provided, deletes from both StaffInfo and StaffEmails
    
    Ensures reference data is cleaned up properly
    '''
    
    param = input("Enter StaffID or Email to delete: ").strip()
    try:
        if param.isdigit():
            cursor.execute("DELETE FROM StaffInfo WHERE StaffID = %s", (int(param),))
        else:
            cursor.execute("DELETE FROM StaffInfo WHERE Email = %s", (param,))
            cursor.execute("DELETE FROM StaffEmails WHERE Email = %s", (param,))
        print("Staff deleted.")
    except mysql.connector.Error as e:
        print("Delete failed:", e)


# ------ Discount info ------

def enter_discount(cursor):
    '''
    Inserts a new discount into the DiscountInfo table
    
    User inputs:
    - Product ID 
    - Discount Description
    - Valid Until Date (YYYY-MM-DD)
    
    '''
    
    product_id = int(input("ProductID: "))
    desc = input("Discount Description: ")
    valid_date = input("Valid Until (YYYY-MM-DD): ")

    try:
        cursor.execute("INSERT INTO DiscountInfo (DiscountDesc, ValidDate, ProductID) VALUES (%s, %s, %s)",
                       (desc, valid_date, product_id))
        print("Discount added.")
    except mysql.connector.Error as e:
        print("Insert failed:", e)


def search_discount(cursor):
    '''
    Searches for a discount by ProductID
    
    Retrieves the discount's description and valid date from the DiscountInfo table
    
    '''
    
    product_id = int(input("Enter Product ID: "))
    cursor.execute("SELECT * FROM DiscountInfo WHERE ProductID = %s", (product_id,))
    result = cursor.fetchone()
    print("Discount Info:", result if result else "No discount found.")


def update_discount(cursor):
    '''
    Updates the description and valid date of a discount for a given ProductID
    
    Prompts User for:
    - Product ID 
    - Discount Description
    - Valid Date (YYYY-MM-DD)
    
    '''
    
    product_id = int(input("Enter Product ID to update: "))
    desc = input("New Discount Description: ")
    valid_date = input("New Valid Date (YYYY-MM-DD): ")

    try:
        cursor.execute("UPDATE DiscountInfo SET DiscountDesc = %s, ValidDate = %s WHERE ProductID = %s",
                       (desc, valid_date, product_id))
        print("Discount updated.")
    except mysql.connector.Error as e:
        print("Update failed:", e)


def delete_discount(cursor):
    '''
    Deletes a discount record for a specific Product ID from the DiscountInfo table
    
    Prompts for:
    - ProductID
    
    Performs a DELETE query
    '''
    
    product_id = int(input("Enter Product ID to delete discount for: "))
    try:
        cursor.execute("DELETE FROM DiscountInfo WHERE ProductID = %s", (product_id,))
        print("Discount deleted.")
    except mysql.connector.Error as e:
        print("Delete failed:", e)


# ------ Inventory Records ------

def update_inventory(cursor):
    '''
    Updates the inventory quantity for a given Product ID and Store ID
    
    - If the product-store exists, it increments the quantity
    - If not, creates a new record in the ProductQuantity table
    
    Prompts user for:
    - Product ID, Store ID
    
    '''
    
    product_id = int(input("Enter Product ID: "))
    store_id = int(input("Enter Store ID: "))
    quantity = int(input("Enter quantity to add or return: "))

    cursor.execute("SELECT InstockQuantity FROM ProductQuantity WHERE ProductID = %s AND StoreID = %s",
                   (product_id, store_id))
    result = cursor.fetchone()
    if result:
        new_qty = result[0] + quantity
        cursor.execute("UPDATE ProductQuantity SET InstockQuantity = %s WHERE ProductID = %s AND StoreID = %s",
                       (new_qty, product_id, store_id))
        print("Inventory updated.")
    else:
        cursor.execute("INSERT INTO ProductQuantity (ProductID, StoreID, InstockQuantity) VALUES (%s, %s, %s)",
                       (product_id, store_id, quantity))
        print("New inventory record added.")


# ------ Reports Info ------

def generate_report(cursor):
    '''
    Generates a simple store-product-customer transaction report
    
    Parameters:
        cursor - Active MySQL cursor
        
    Returns:
        None
    '''
    
    print("\nGenerating report...")

    try:
        cursor.execute("""
            SELECT 
                pq.StoreID,
                pq.InStockQuantity,
                pq.ProductID,
                t.PurchaseDate,
                t.CustomerID AS CustomerIDDoesTransaction,
                t.TotalPrice,
                s.StoreAddr,
                p.ProductName,
                c.CustomerID,
                c.CustomerName
            FROM 
                ProductQuantity pq
            JOIN Transactions t ON pq.ProductID = t.ProductID AND pq.StoreID = t.StoreID
            JOIN Store s ON pq.StoreID = s.StoreID
            JOIN Product p ON pq.ProductID = p.ProductID
            JOIN Customer c ON t.CustomerID = c.CustomerID
            ORDER BY t.PurchaseDate DESC
        """)

        results = cursor.fetchall()
        if not results:
            print("No report data found.")
            return

        for row in results:
            print(f"StoreID: {row[0]}, InStock: {row[1]}, ProductID: {row[2]}, Date: {row[3]}, "
                  f"TxnCustomerID: {row[4]}, Price: ${row[5]:.2f}, StoreAddr: {row[6]}, "
                  f"Product: {row[7]}, CustomerID: {row[8]}, Name: {row[9]}")
    except mysql.connector.Error as e:
        print("Error generating report:", e)
