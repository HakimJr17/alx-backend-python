import mysql.connector
from decimal import Decimal

# =========================================================================
# 1. DATABASE CONFIGURATION & PLUMBING
# =========================================================================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_mysql_root_password"  # This should be replaced with the actual password
DB_NAME = "ALX_prodev"

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# =========================================================================
# 2. AGE STREAMER GENERATOR (LOOP 1)
# =========================================================================

def stream_user_ages():
    """
    Generator that fetches and yields user ages one by one from the database.
    
    This function uses a single loop to lazily fetch data.
    
    Yields:
        Decimal: The age of a single user.
    """
    conn = None
    cursor = None
    try:
        conn = connect_to_prodev()
        if not conn:
            return

        # Use unbuffered cursor for maximum memory efficiency with fetchone()
        cursor = conn.cursor(dictionary=True, buffered=False)
        
        # NOTE: Explicitly selecting only the age field for efficiency
        select_sql = "SELECT age FROM user_data"
        cursor.execute(select_sql)

        # LOOP 1: Fetches ages one row at a time until the end of the result set
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            
            # Yields the age value (already a Decimal type from the database)
            yield row['age']

    except mysql.connector.Error as err:
        print(f"Error streaming ages: {err}")

    finally:
        # Crucial to release resources
        if cursor: cursor.close()
        if conn: conn.close()

# =========================================================================
# 3. AGGREGATION FUNCTION (LOOP 2)
# =========================================================================

def calculate_average_age():
    """
    Consumes the age generator to calculate the average age without loading 
    the entire dataset into memory.
    
    This function contains the second and final loop of the script.
    """
    # Initialize trackers using Decimal for precision
    total_sum_of_ages = Decimal('0')
    total_count_of_users = 0
    
    # Get the age streamer (the generator object)
    age_stream = stream_user_ages()

    # LOOP 2: Iterates over the generator, consuming ages one by one
    for age in age_stream:
        total_sum_of_ages += age
        total_count_of_users += 1
        
    # Check to prevent ZeroDivisionError
    if total_count_of_users == 0:
        return None
        
    # Calculate the final average outside the loop
    average_age = total_sum_of_ages / Decimal(total_count_of_users)
    return average_age

# =========================================================================
# 4. EXECUTION BLOCK
# =========================================================================

if __name__ == "__main__":
    
    average_age = calculate_average_age()
    
    if average_age is not None:
        # Format the output to two decimal places
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No user data found to calculate the average age.")
