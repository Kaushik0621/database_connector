import sqlite3

# Path to the database file
db_path = 'instance/material.db'

# Connect to the SQLite database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Get the list of tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in color.db:")
for table in tables:
    print(f"- {table[0]}")

# For each table, print the data
for table in tables:
    table_name = table[0]
    print(f"\nData in table '{table_name}':")
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print(column_names)
    for row in rows:
        print(row)

# Close the connection
connection.close()
