import mysql.connector
import getpass

# Ask the user for database info
user = input("Enter MySQL username: ")
password = getpass.getpass("Enter MySQL password: ")

# Connect using the entered info
connection = mysql.connector.connect(
    host="localhost",
    user=user,
    password=password,
    database="muskieco"
)

cursor = connection.cursor()
cursor.execute("SHOW TABLES")

for table in cursor.fetchall():
    print(table)

cursor.close()
connection.close()
