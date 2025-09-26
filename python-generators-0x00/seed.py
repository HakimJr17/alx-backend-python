import mysql.connector
import uuid
import csv
from decimal import Decimal

# --- 1. Database Configuration ---
# The DB_PASSWORD attribute should be assigned the actual MySQL credentials
DB_HOST = "localhost"
DB_USER = "root"  # Use the root user that worked for you
DB_PASSWORD = "your_mysql_root_password" 
DB_NAME = "ALX_prodev"
CSV_FILE = "user_data.csv"

# --- 2. Connection and Setup Functions ---

def connect_db(database=None):
    """Connects to the MySQL database server."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=database # If None, connects to the server
        )
        print(f"Connection successful to: {database if database else 'Server'}")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def create_database(connection):
    """Creates the database ALX_prodev if it does not exist."""
    try:
        cursor = connection.cursor()
        # SQL to create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' ensured.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL."""
    return connect_db(database=DB_NAME)

def create_table(connection):
    """Creates a table user_data if it does not exists with the required fields."""
    try:
        cursor = connection.cursor()
        # SQL to create the user_data table with specified schema
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5, 2) NOT NULL
        )
        """
        cursor.execute(table_sql)
        print("Table 'user_data' ensured.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

# --- 3. Data Insertion Function ---

def insert_data(connection, data):
    """Inserts data in the database if it does not exist."""
    if not data:
        return

    cursor = connection.cursor()
    # Check for existing data by email to prevent duplicate insertion
    check_sql = "SELECT user_id FROM user_data WHERE email = %s"
    insert_sql = "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
    
    insert_count = 0
    
    for row in data:
        # Check if user already exists
        cursor.execute(check_sql, (row['email'],))
        if cursor.fetchone() is None:
            # Data validation and preparation
            new_uuid = str(uuid.uuid4())
            values = (new_uuid, row['name'], row['email'], row['age'])
            
            try:
                cursor.execute(insert_sql, values)
                insert_count += 1
            except mysql.connector.Error as err:
                print(f"Error inserting data for {row['name']}: {err}")
                connection.rollback()
    
    connection.commit()
    print(f"Successfully inserted {insert_count} new records.")
    cursor.close()

# --- 4. Main Execution Block ---

def load_data_from_csv(file_path):
    """Helper function to read and transform data from the CSV file."""
    data = []
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Transformation: Convert age to Decimal as required by the schema
                    row['age'] = Decimal(row['age'])
                    data.append(row)
                except ValueError:
                    print(f"Skipping row due to invalid age value: {row}")
                    continue
    except FileNotFoundError:
        print(f"Error: CSV file not found at {file_path}")
    return data

if __name__ == "__main__":
    # 1. Connect to the server (no database specified yet)
    server_conn = connect_db()
    if not server_conn:
        exit(1)

    # 2. Create the required database
    create_database(server_conn)
    server_conn.close()

    # 3. Connect to the newly created/ensured database
    db_conn = connect_to_prodev()
    if not db_conn:
        exit(1)

    # 4. Create the required table
    create_table(db_conn)

    # 5. Load data from CSV file
    user_data = load_data_from_csv(CSV_FILE)

    # 6. Insert data into the table
    insert_data(db_conn, user_data)
    
    # 7. Close the connection
    db_conn.close()
    print("Database seeding complete.")