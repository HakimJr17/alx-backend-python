## 💾 Data Pipeline Documentation: Initial User Data Load

This section documents the end-to-end process for the initial bulk data load into the `users` table, including the technical resolutions required and a comparison to programmatic solutions.

### 1. The Executed Pipeline: Manual SQL Bulk Load

Our initial process implemented a **Manual ETL Pipeline** to move data from a remote source to the local MySQL database.

| Stage | Action & Command Executed | Notes |
| :--- | :--- | :--- |
| **Extraction (E)** | `curl -o user_data.csv "[URL]"` | Downloads the raw data to the project directory. |
| **Plumbing** | `/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql" -u root -p` | **Connection Fix:** Used absolute path to resolve `command not found` and connected as **`root`** to bypass `Access denied` (lacking `FILE` privilege). |
| **Server Config** | (In MySQL Monitor): `SET GLOBAL local_infile = true;` | Explicitly enables server-side permission for local file transfer. |
| **Transformation & Loading (T/L)** | `LOAD DATA LOCAL INFILE ... IGNORE 1 ROWS;` | Uses SQL's native bulk function. The `IGNORE 1 ROWS` clause handles the transformation (filtering out the header). |

### 2. Alternative Approach: Programmatic ETL Pipeline

For future reference and enterprise-level stability, the recommended approach is a **Programmatic (Scripted) ETL Pipeline** using a language like Python.

**Prototype Examples (from the proposed `seed.py`):**

* `def connect_db()`
* `def create_table(connection)`
* `def insert_data(connection, data)`

### 3. Key Differences Between Approaches

| Feature | Manual SQL (`LOAD DATA`) | Programmatic Python Script |
| :--- | :--- | :--- |

| **Transformation** | Limited (splitting by comma, skipping rows). | **Unlimited.** Can perform complex data cleaning, validation (e.g., email format), and calculations *before* insertion. |

| **Data Flow** | Single, highly optimized **Bulk** operation. | **Row-by-Row** or batch insertion handled by the script. Slower, but more controllable. |

| **Error Handling** | Basic. Entire command may fail or silently skip bad rows. | **Robust.** Script can log exactly which row failed, why, and implement logic to correct or skip the error gracefully. |

| **Setup Automation** | Requires separate manual SQL commands for database/table creation. | **Fully Automated.** The script handles checking/creating the database and table schema automatically. |

| **Use Case** | Quick, one-time loads of clean data where transformation is minimal. | Production environments, complex datasets, high data quality requirements, and recurring tasks. |