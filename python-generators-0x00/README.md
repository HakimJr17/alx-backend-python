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

For future reference and enterprise-level stability, the recommended approach is a **Programmatic (Scripted) ETL Pipeline** using a language like Python (as implemented in `seed.py`).

| Feature | Manual SQL (`LOAD DATA`) | Programmatic Python Script (`seed.py`) |
| :--- | :--- | :--- |
| **Transformation** | Limited (splitting by comma, skipping rows). | **Unlimited.** Can perform complex data cleaning, validation (e.g., email format), and calculations *before* insertion. |
| **Data Flow** | Single, highly optimized **Bulk** operation. | **Row-by-Row** or batch insertion handled by the script. Slower, but more controllable. |
| **Error Handling** | Basic. Entire command may fail or silently skip bad rows. | **Robust.** Script can log exactly which row failed, why, and implement logic to correct or skip the error gracefully. |

---

## 📈 Conceptual Deep Dive: Scaling Data Access with Generators

This section documents the transition from simple data loading to memory-efficient data streaming using Python generators (`yield`).

### 3. Generator Implementation (Lazy Loading)

We implemented three levels of memory efficiency using generators:

| File | Generator Type | Purpose | Key SQL/Python Technique |
| :--- | :--- | :--- | :--- |
| `seed.py` | Single-Row Stream (`stream_users`) | Fetches one record at a time, holding minimal data in memory. | Uses `cursor.fetchone()` and `yield`. |
| `1-batch_processing.py` | Batch Stream (`stream_users_in_batches`) | Fetches data in fixed-size chunks to optimize performance for processing. | Uses `cursor.fetchmany(size=N)` and `yield`. |
| `2-lazy_paginate.py` | Lazy Pagination (`lazy_paginate`) | Simulates fetching data page-by-page, primarily for front-end display. | Uses SQL's `LIMIT` and `OFFSET`. |

### 4. The Essence of Lazy Pagination (LIMIT and OFFSET)

Pagination is the mechanism that allows websites (like video feeds or search results) to display small chunks of data and load more only when you click "Next Page."

The key is the combination of two SQL clauses:

* **`LIMIT`:** Defines the **page size** (e.g., how many records to fetch).
* **`OFFSET`:** Defines the **starting point** of the fetch by telling the database how many prior records to skip.

| Action (User Clicks) | SQL Query Example (10 Records per Page) | Database Action |
| :--- | :--- | :--- |
| **Page 1 (First Load)** | `LIMIT 10 OFFSET 0` | Starts at record 1, fetches the next 10. |
| **Page 2** | `LIMIT 10 OFFSET 10` | **Skips the first 10** records, fetches the next 10 (records 11-20). |
| **Page 3** | `LIMIT 10 OFFSET 20` | **Skips the first 20** records, fetches the next 10 (records 21-30). |

**Conclusion:** Using `OFFSET` prevents the database from wasting resources by fetching and sending the records that the user has already seen or that have already been processed. Your Python generator simply automates the calculation of that required `OFFSET` number for each page!