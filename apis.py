import sqlite3


# ------ Start of information processing ------

# ------ Store info ------

# store id is auto-incrementing
def enter_store(cursor):
    store_addr = input("Enter store address: ").strip()
    phone = input("Enter store phone #: ").strip()

    try:
        cursor.execute("INSERT INTO StoreAddress (StoreAddr, Phone) VALUES (?, ?)", (store_addr, phone))
        cursor.execute("INSERT INTO Store (StoreAddr) VALUES (?)", (store_addr,))
        print("Store added successfully.")
    except sqlite3.Error as e:
        print(f"Error: {e}")


def search_store(cursor):
    store_id = input("Enter Store ID (or press Enter to skip): ").strip()
    store_addr = input("Enter Store Address (or press Enter to skip): ").strip()

    query = "SELECT Store.StoreID, Store.StoreAddr, StoreAddress.Phone FROM Store JOIN StoreAddress ON Store.StoreAddr = StoreAddress.StoreAddr WHERE 1=1"
    params = []
    if store_id:
        query += " AND Store.StoreID = ?"
        params.append(store_id)
    if store_addr:
        query += " AND Store.StoreAddr = ?"
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

    # get current store info
    cursor.execute("SELECT StoreAddr FROM Store WHERE StoreID = ?", (store_id,))
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
            # prevent address conflict
            cursor.execute("SELECT 1 FROM StoreAddress WHERE StoreAddr = ?", (new_addr,))
            if cursor.fetchone():
                print("That address already exists. Please update the phone separately if needed.")
                return

            # copy current phone if new phone not provided
            if not phone_changed:
                cursor.execute("SELECT Phone FROM StoreAddress WHERE StoreAddr = ?", (current_addr,))
                phone_row = cursor.fetchone()
                new_phone = phone_row[0] if phone_row else "000-000-0000"

            # insert the new address
            cursor.execute("INSERT INTO StoreAddress (StoreAddr, Phone) VALUES (?, ?)", (new_addr, new_phone))

            # update Store to use new address
            cursor.execute("UPDATE Store SET StoreAddr = ? WHERE StoreID = ?", (new_addr, store_id))
            print("Store address updated.")

            # delete old address if no other stores use it
            cursor.execute("SELECT COUNT(*) FROM Store WHERE StoreAddr = ?", (current_addr,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM StoreAddress WHERE StoreAddr = ?", (current_addr,))
                print("Old address deleted (no longer used).")

        elif phone_changed:
            # update phone for the current address
            cursor.execute("UPDATE StoreAddress SET Phone = ? WHERE StoreAddr = ?", (new_phone, current_addr))
            print("Phone number updated.")

        else:
            print("No changes made.")

    except sqlite3.Error as e:
        print(f"Update failed: {e}")


def delete_store(cursor):
    store_id = input("Enter Store ID to delete: ").strip()

    try:
        # get the store address from the Store ID
        cursor.execute("SELECT StoreAddr FROM Store WHERE StoreID = ?", (store_id,))
        result = cursor.fetchone()

        if not result:
            print("No store found with that ID.")
            return

        store_addr = result[0]

        # delete from Store table
        cursor.execute("DELETE FROM Store WHERE StoreID = ?", (store_id,))

        # then delete from StoreAddress
        cursor.execute("DELETE FROM StoreAddress WHERE StoreAddr = ?", (store_addr,))

        print("Store and its address deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting store: {e}")


# ------ Member info ------


def enter_member(cursor):
    customer_id = int(input("CustomerID: "))
    email = input("Email: ")
    # phone = input("Phone #: ") - don't have a phone column in that table
    home_addr = input("Home Address: ")
    active = input("Active? (yes/no): ").lower() == "yes"
    reward_points = int(input("Rewards Points: "))
    staff_id = int(input("Staff ID sending notice: "))

    try:
        cursor.execute("INSERT INTO CustomerEmail (Email, CustomerName, HomeAddr, ActivateStatus, StaffIDSendsNotice, RewardPoints) VALUES (?, ?, ?, ?, ?, ?)",
                       (email, email.split("@")[0], home_addr, active, staff_id, reward_points))
        cursor.execute("INSERT INTO MemberInfo (CustomerID, Email) VALUES (?, ?)", (customer_id, email))
        print("Member entered successfully.")
    except sqlite3.Error as e:
        print("Error entering member:", e)


def search_member(cursor):
    query = "SELECT CustomerID, Email, HomeAddr, ActivateStatus, StaffIDSendsNotice, RewardPoints FROM CustomerEmail JOIN MemberInfo USING(Email)"
    param = input("Enter CustomerID or Email: ").strip()
    if param.isdigit():
        cursor.execute(query + " WHERE CustomerID = ?", (int(param),))
    else:
        cursor.execute(query + " WHERE Email = ?", (param,))
    result = cursor.fetchone()
    if result:
        print("Member Info:", result)
    else:
        print("No member found.")


def update_member(cursor):
    customer_id = int(input("CustomerID to update: "))

    # Look up email from MemberInfo
    cursor.execute("SELECT Email FROM MemberInfo WHERE CustomerID = ?", (customer_id,))
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
        cursor.execute("""
            UPDATE CustomerEmail 
            SET HomeAddr = ?, ActivateStatus = ?, StaffIDSendsNotice = ?, RewardPoints = ?
            WHERE Email = ?""", (home_addr, active, staff_id, reward_points, email)
            )
        print("Member updated.")
    except sqlite3.Error as e:
        print(f"Update failed: {e}")


def delete_member(cursor):
    param = input("Enter CustomerID or Email to delete: ").strip()
    try:
        if param.isdigit():
            cursor.execute("DELETE FROM MemberInfo WHERE CustomerID = ?", (int(param),))
        else:
            cursor.execute("DELETE FROM MemberInfo WHERE Email = ?", (param,))
            cursor.execute("DELETE FROM CustomerEmail WHERE Email = ?", (param,))
        print("Member deleted.")
    except sqlite3.Error as e:
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
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                       (staff_id, name, age, addr, job, email, date, signups))
        cursor.execute("INSERT INTO StaffInfo (StaffID, Email) VALUES (?, ?)", (staff_id, email))
        print("Staff entered.")
    except sqlite3.Error as e:
        print("Insert failed:", e)


def search_staff(cursor):
    param = input("Enter StaffID or Email: ").strip()
    query = """SELECT StaffID, StaffIDHasStore, StaffName, Age, HomeAddr, 
               JobTitle, Email, TimeOfEmployment, NumberOfSignUps 
               FROM StaffEmails JOIN StaffInfo USING(Email)"""

    if param.isdigit():
        cursor.execute(query + " WHERE StaffID = ?", (int(param),))
    else:
        cursor.execute(query + " WHERE Email = ?", (param,))
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
        cursor.execute("""UPDATE StaffEmails SET StaffIDHasStore=?, StaffName=?, Age=?, HomeAddr=?, 
                          JobTitle=?, TimeOfEmployment=?, NumberOfSignUps=? WHERE Email=?""",
                       (staff_id, name, age, addr, job, date, signups, email))
        print("Staff updated.")
    except sqlite3.Error as e:
        print("Update failed:", e)


def delete_staff(cursor):
    param = input("Enter StaffID or Email to delete: ").strip()
    try:
        if param.isdigit():
            cursor.execute("DELETE FROM StaffInfo WHERE StaffID = ?", (int(param),))
        else:
            cursor.execute("DELETE FROM StaffInfo WHERE Email = ?", (param,))
            cursor.execute("DELETE FROM StaffEmails WHERE Email = ?", (param,))
        print("Staff deleted.")
    except sqlite3.Error as e:
        print("Delete failed:", e)


# ------ Discount info ------


def enter_discount(cursor):
    product_id = int(input("ProductID: "))
    desc = input("Discount Description: ")
    valid_date = input("Valid Until (YYYY-MM-DD): ")

    try:
        cursor.execute("INSERT INTO DiscountInfo (DiscountDesc, ValidDate, ProductID) VALUES (?, ?, ?)",
                       (desc, valid_date, product_id))
        print("Discount added.")
    except sqlite3.Error as e:
        print("Insert failed:", e)


def search_discount(cursor):
    product_id = int(input("Enter Product ID: "))
    cursor.execute("SELECT * FROM DiscountInfo WHERE ProductID = ?", (product_id,))
    result = cursor.fetchone()
    print("Discount Info:", result if result else "No discount found.")


def update_discount(cursor):
    product_id = int(input("Enter Product ID to update: "))
    desc = input("New Discount Description: ")
    valid_date = input("New Valid Date (YYYY-MM-DD): ")

    try:
        cursor.execute("UPDATE DiscountInfo SET DiscountDesc = ?, ValidDate = ? WHERE ProductID = ?",
                       (desc, valid_date, product_id))
        print("Discount updated.")
    except sqlite3.Error as e:
        print("Update failed:", e)


def delete_discount(cursor):
    product_id = int(input("Enter Product ID to delete discount for: "))
    try:
        cursor.execute("DELETE FROM DiscountInfo WHERE ProductID = ?", (product_id,))
        print("Discount deleted.")
    except sqlite3.Error as e:
        print("Delete failed:", e)


# ------ End of information processing ------


# ------ Start of maintaining inventory records ------


def update_inventory(cursor):
    product_id = int(input("Enter Product ID: "))
    store_id = int(input("Enter Store ID: "))
    quantity = int(input("Enter quantity to add or return: "))

    # Try to update first
    cursor.execute("SELECT InstockQuantity FROM ProductQuantity WHERE ProductID = ? AND StoreID = ?", (product_id, store_id))
    result = cursor.fetchone()
    if result:
        new_qty = result[0] + quantity
        cursor.execute("UPDATE ProductQuantity SET InstockQuantity = ? WHERE ProductID = ? AND StoreID = ?", (new_qty, product_id, store_id))
        print("Inventory updated.")
    else:
        cursor.execute("INSERT INTO ProductQuantity (ProductID, StoreID, InstockQuantity) VALUES (?, ?, ?)", (product_id, store_id, quantity))
        print("New inventory record added.")


# ------ End of maintaining inventory records ------
