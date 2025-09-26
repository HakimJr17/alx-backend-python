import mysql.connector
from decimal import Decimal

# =========================================================================
# 1. DATABASE CONFIGURATION & PLUMBING (Copied from seed.py for runnability)
# =========================================================================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_mysql_root_password"  # This should be replaced with the actual password
DB_NAME = "ALX_prodev"
TABLE_NAME = "user_data"

def connect_db(database=None):
    """Connects to the MySQL database server."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=database 
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL."""
    return connect_db(database=DB_NAME)

# =========================================================================
# 2. BATCH GENERATOR (PROTOYPE: stream_users_in_batches(batch_size))
# =========================================================================

def stream_users_in_batches(batch_size):
    """
    Generator function that streams data from the table in fixed-size batches.
    
    This adheres to the constraint of using only one loop in the generator 
    to fetch data using cursor.fetchmany().
    
    Args:
        batch_size (int): The number of rows to fetch in each batch.
    
    Yields:
        list: A list of dictionaries representing a batch of user records.
    """
    conn = None
    cursor = None
    try:
        conn = connect_to_prodev()
        if not conn:
            return

        # Cursor configured to fetch results as dictionaries
        cursor = conn.cursor(dictionary=True) 
        select_sql = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(select_sql)

        # LOOP 1 (Required Loop): Fetch and yield batches until fetchmany returns an empty list
        while True: 
            # fetchmany retrieves the specified number of rows (the batch)
            batch = cursor.fetchmany(size=batch_size)
            if not batch:
                break
            yield batch # Yields the list/batch, pausing execution
            
    except mysql.connector.Error as err:
        print(f"Error streaming batches: {err}")

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# =========================================================================
# 3. BATCH PROCESSING (PROTOYPE: batch_processing(batch_size))
# =========================================================================

def batch_processing(batch_size):
    """
    Processes each batch of users streamed from the database.
    
    Filters records to find users whose age is greater than 25.
    
    The entire processing path uses exactly 3 loops:
    1. while True in stream_users_in_batches()
    2. for batch in stream_users_in_batches()
    3. for user in batch
    
    Args:
        batch_size (int): The size of the batch to stream.
    """
    print(f"\n--- Starting Batch Processing (Batch Size: {batch_size}) ---")
    
    total_users = 0
    filtered_users = 0
    
    # LOOP 2: Consumes the batch generator, getting one batch (list) at a time
    for batch in stream_users_in_batches(batch_size):
        total_users += len(batch)
        print(f"Received batch of size: {len(batch)}.")
        
        # LOOP 3: Processes/filters rows within the current batch
        for user in batch: 
            # Ensure age is compared against a Decimal value for correctness
            if user['age'] > Decimal('25'):
                filtered_users += 1
                print(f" -> FILTERED: {user['name']} (Age: {user['age']})")
                
    print(f"\nBatch Processing Complete.")
    print(f"Total Users Examined: {total_users}")
    print(f"Users Filtered (Age > 25): {filtered_users}")

# =========================================================================
# 4. EXECUTION BLOCK
# =========================================================================

if __name__ == "__main__":
    # NOTE: This block assumes the 'ALX_prodev' database and 'user_data' table 
    # have already been created and populated by seed.py.
    
    BATCH_SIZE = 10
    batch_processing(BATCH_SIZE)
