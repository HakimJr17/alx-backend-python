import mysql.connector
import time

# =========================================================================
# 1. DATABASE CONFIGURATION & PLUMBING
# =========================================================================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_mysql_root_password"  # THis should be replaced with the correct password
DB_NAME = "ALX_prodev"

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
# 2. PAGINATION HELPER FUNCTION (Executes one query)
# =========================================================================

def paginate_users(page_size, offset):
    """
    Fetches a single page of user data using SQL LIMIT and OFFSET.
    
    Args:
        page_size (int): The number of records to retrieve (LIMIT).
        offset (int): The starting position in the full result set (OFFSET).
        
    Returns:
        list: A list of dictionaries representing one page of data.
    """
    conn = None
    cursor = None
    page_data = []
    
    try:
        conn = connect_to_prodev()
        if not conn:
            return page_data

        cursor = conn.cursor(dictionary=True)
        
        # Hardcoding 'user_data' as required by the checker.
        # This query structure is the key to fetching paginated data efficiently.
        select_sql = f"SELECT user_id, name, email, age FROM user_data LIMIT {page_size} OFFSET {offset}"
        
        cursor.execute(select_sql)
        page_data = cursor.fetchall() # Fetches the entire page (list)
        return page_data

    except mysql.connector.Error as err:
        print(f"Error fetching page at offset {offset}: {err}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# =========================================================================
# 3. LAZY PAGINATOR GENERATOR (PROTOYPE: lazy_paginate(page_size))
# =========================================================================

def lazy_paginate(page_size):
    """
    Generator that lazily fetches and yields data from user_data page by page.
    
    This function adheres to the constraint of using only one loop.
    
    Args:
        page_size (int): The number of records per page.
    
    Yields:
        list: A list of dictionaries representing a single page of user records.
    """
    offset = 0
    
    # LOOP 1 (The required single loop): Fetches pages until an empty page is returned
    while True:
        # 1. FETCH: Get the next page of data
        page = paginate_users(page_size, offset)
        
        # 2. BREAK CONDITION: If the list is empty, we have reached the end of the table
        if not page:
            break
            
        # 3. YIELD: Send the page data back to the caller
        yield page
        
        # 4. INCREMENT: Prepare the offset for the next page request
        offset += page_size


# =========================================================================
# 4. EXECUTION BLOCK (Demonstration)
# =========================================================================

if __name__ == "__main__":
    PAGE_SIZE = 7 # Set a page size for demonstration
    
    print("--- Starting Lazy Pagination Demonstration ---")
    print(f"Fetching pages with PAGE_SIZE = {PAGE_SIZE}")

    page_generator = lazy_paginate(PAGE_SIZE)
    page_count = 0

    # Consuming the generator proves the lazy loading
    for page in page_generator:
        page_count += 1
        
        # Simulate heavy processing (pauses only after receiving the whole page)
        time.sleep(0.1) 
        
        print("-" * 30)
        print(f"--> YIELDED PAGE {page_count} (Records: {len(page)})")
        print(f"    Current Offset: {(page_count - 1) * PAGE_SIZE}")
        print(f"    First user on page: {page[0]['name']}")
    
    print("-" * 30)
    print(f"Lazy Pagination Complete. Total pages processed: {page_count}")
