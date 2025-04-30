import mysql.connector

# ------ Start of information processing ------

# ------ Store info ------

def enter_store(cursor):
    store_addr = input("Enter store address: ").strip()
    phone = input("Enter store phone #: ").strip()

    try:
        cursor.execute("INSERT INTO StoreAddress (StoreAddr, Phone) VALUES (%s, %s)", (store_addr, phone))
        cursor.execute("INSERT INTO Store (StoreAddr) VALUES (%s)", (store_addr,))
        print("Store added successfully.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")


def search_store(cursor):
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

    except mysql.connector.Error as e:
        print(f"Update failed: {e}")


def delete_store(cursor):
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
    except mysql.connector.Error as e:
        print("Error entering member:", e)


def search_member(cursor):
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
        print("Member updated.")
    except mysql.connector.Error as e:
        print(f"Update failed: {e}")


def delete_member(cursor):
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
    product_id = int(input("Enter Product ID: "))
    cursor.execute("SELECT * FROM DiscountInfo WHERE ProductID = %s", (product_id,))
    result = cursor.fetchone()
    print("Discount Info:", result if result else "No discount found.")


def update_discount(cursor):
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
    product_id = int(input("Enter Product ID to delete discount for: "))
    try:
        cursor.execute("DELETE FROM DiscountInfo WHERE ProductID = %s", (product_id,))
        print("Discount deleted.")
    except mysql.connector.Error as e:
        print("Delete failed:", e)


# ------ Inventory Records ------

def update_inventory(cursor):
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

        