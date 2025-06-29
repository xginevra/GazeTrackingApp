import sqlite3
from pathlib import Path

def create_database():
    
    # Define the path to the app directory and database
    db_path = Path('gazedata.db')

    # Connect to the database
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # SQL command to create the 'venues' table if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS times (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forehead FLOAT,
        eyes FLOAT,
        nose FLOAT,
        mouth FLOAT,
        chin FLOAT
    ) """
    
    # Execute the SQL command
    cursor.execute(create_table_sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_data_sql(forehead, eyes, nose, mouth, chin):
# Define the path to the app directory and database
    db_path = 'gazedata.db'

    # Connect to the database
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    # SQL command to insert data into the 'venues' table
    insert_sql = """
    INSERT INTO times (forehead, eyes, nose, mouth, chin)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(insert_sql, (forehead, eyes, nose, mouth, chin))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("gaze data inserted successfully.")