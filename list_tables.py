import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("site.db")

# Create a cursor object
cursor = conn.cursor()

# Execute a query to retrieve all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Fetch all results
tables = cursor.fetchall()

# Print table names
print("Tables in the SQLite database:")
for table in tables:
    print(table[0])

# Close the connection
conn.close()
