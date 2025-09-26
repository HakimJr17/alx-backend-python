import mysql.connector
from .seed import connect_to_prodev

# NOTE: This file assumes the following dependencies are available in the running environment:
# 1. TABLE_NAME constant (set to "user_data")
# 2. connect_to_prodev() function (defined in seed.py) which returns a valid database connection.

TABLE_NAME = "user_data" 

def stream_users():
    """
    Uses a Python generator (yield) to stream rows one by one from the 
    user_data table, ensuring memory efficiency by processing one record 
    at a time without loading the entire result set into memory.
    
    Yields:
        dict: A single user record (user_id, name, email, age) from the database.
    """
    conn = None
    cursor = None
    try:
        # Connect to the target database (Dependency on connect_to_prodev)
        conn = connect_to_prodev()
        if not conn:
            # If connection fails, the generator terminates gracefully
            return 
        
        # Use dictionary=True to fetch results as dictionaries (keys are column names)
        cursor = conn.cursor(dictionary=True) 
        
        # Execute the query
        select_sql = f"SELECT user_id, name, email, age FROM {TABLE_NAME}"
        cursor.execute(select_sql)
        
        # --- THE SINGLE LOOP ---
        # Fetch one row at a time and yield it immediately
        while True:
            row = cursor.fetchone()
            if row is None:
                break # Exit the loop when no more rows are returned
            yield row
        
    except mysql.connector.Error as err:
        print(f"Error streaming data: {err}")
        
    finally:
        # Crucial: Ensure database resources are closed in the 'finally' block
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    print("This file contains the generator function 'stream_users'.")
    print("To test, ensure 'connect_to_prodev()' is defined and working.")
