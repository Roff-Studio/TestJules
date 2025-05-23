# src/database_manager.py
import sqlite3
import os
from datetime import datetime

# Define database path and directory
DATABASE_DIR = "data"
DATABASE_PATH = os.path.join(DATABASE_DIR, "memecoins.db")

def initialize_database():
    """
    Initializes the database and creates the necessary tables if they don't exist.
    """
    print(f"Attempting to initialize database at {DATABASE_PATH}...")
    try:
        # Ensure the database directory exists
        os.makedirs(DATABASE_DIR, exist_ok=True)
        print(f"Directory '{DATABASE_DIR}' ensured.")

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        print("Database connection established.")

        # Create 'coins' table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS coins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_address TEXT UNIQUE NOT NULL,
            name TEXT,
            symbol TEXT,
            creation_timestamp DATETIME,
            source_twitter_handle TEXT,
            first_seen_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("Table 'coins' schema checked/created.")

        # Create 'snapshots' table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            market_cap REAL,
            reply_count_x INTEGER,
            retweet_count_x INTEGER,
            mention_count_xai INTEGER,
            pumpfun_volume_usd REAL,
            pumpfun_market_cap_usd REAL,
            FOREIGN KEY (coin_id) REFERENCES coins (id)
        )
        """)
        print("Table 'snapshots' schema checked/created.")

        conn.commit()
        print("Database changes committed.")
    except sqlite3.Error as e:
        print(f"SQLite error during initialization: {e}")
    except OSError as e:
        print(f"OS error during directory creation: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")
    print("Database initialization process complete.")

def add_coin(token_address: str, name: str = None, symbol: str = None, 
             creation_timestamp: datetime = None, source_twitter_handle: str = None) -> int | None:
    """
    Adds a new coin to the 'coins' table or ignores if token_address already exists.

    Returns:
        The ID of the inserted row, or None if an error occurs or the row was ignored (and ID not retrievable that way).
    """
    print(f"Attempting to add coin with token_address: {token_address}")
    inserted_id = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Convert datetime to string if provided
        creation_ts_str = creation_timestamp.isoformat() if creation_timestamp else None

        cursor.execute("""
        INSERT OR IGNORE INTO coins (token_address, name, symbol, creation_timestamp, source_twitter_handle)
        VALUES (?, ?, ?, ?, ?)
        """, (token_address, name, symbol, creation_ts_str, source_twitter_handle))
        
        conn.commit()
        
        if cursor.rowcount > 0: # Check if a row was actually inserted
            inserted_id = cursor.lastrowid
            print(f"Coin '{token_address}' inserted with ID: {inserted_id}")
        else:
            print(f"Coin '{token_address}' already exists or no change made.")
            # If it already exists, we might want to fetch its ID
            cursor.execute("SELECT id FROM coins WHERE token_address = ?", (token_address,))
            result = cursor.fetchone()
            if result:
                inserted_id = result[0]
                print(f"Existing coin '{token_address}' found with ID: {inserted_id}")


    except sqlite3.Error as e:
        print(f"SQLite error in add_coin for {token_address}: {e}")
    finally:
        if conn:
            conn.close()
    return inserted_id

def add_snapshot(coin_id: int, market_cap: float = None, reply_count_x: int = None, 
                 retweet_count_x: int = None, mention_count_xai: int = None, 
                 pumpfun_volume_usd: float = None, pumpfun_market_cap_usd: float = None) -> int | None:
    """
    Adds a new snapshot for a coin to the 'snapshots' table.

    Returns:
        The ID of the inserted row, or None if an error occurs.
    """
    print(f"Attempting to add snapshot for coin_id: {coin_id}")
    inserted_id = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO snapshots (coin_id, market_cap, reply_count_x, retweet_count_x, 
                               mention_count_xai, pumpfun_volume_usd, pumpfun_market_cap_usd)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (coin_id, market_cap, reply_count_x, retweet_count_x, 
              mention_count_xai, pumpfun_volume_usd, pumpfun_market_cap_usd))
        
        conn.commit()
        inserted_id = cursor.lastrowid
        print(f"Snapshot for coin_id {coin_id} added with ID: {inserted_id}")

    except sqlite3.Error as e:
        print(f"SQLite error in add_snapshot for coin_id {coin_id}: {e}")
    finally:
        if conn:
            conn.close()
    return inserted_id

if __name__ == '__main__':
    print("\n--- Running database_manager.py tests ---")
    
    # 1. Initialize database
    initialize_database()
    
    print("\n--- Testing add_coin ---")
    # 2. Add a sample coin
    sample_token_address = "SOL_TOKEN_ADDRESS_EXAMPLE_12345"
    coin_name = "TestCoin"
    coin_symbol = "TST"
    # Using datetime object for creation_timestamp
    coin_creation_ts = datetime(2024, 1, 1, 12, 0, 0) 
    twitter_handle = "@TestCoinHandle"
    
    coin_id = add_coin(sample_token_address, coin_name, coin_symbol, coin_creation_ts, twitter_handle)
    if coin_id:
        print(f"add_coin returned ID: {coin_id} for {sample_token_address}")
    else:
        print(f"Failed to add coin or coin already exists: {sample_token_address}")

    # Try adding the same coin again to test OR IGNORE
    print("\n--- Testing add_coin (duplicate) ---")
    coin_id_duplicate_attempt = add_coin(sample_token_address, coin_name, coin_symbol, coin_creation_ts, twitter_handle)
    if coin_id_duplicate_attempt:
        print(f"add_coin (duplicate) returned ID: {coin_id_duplicate_attempt} for {sample_token_address} (should be existing ID)")
    else:
        print(f"Failed to add coin (duplicate) or error: {sample_token_address}")


    # 3. Add a snapshot for the coin (only if coin_id was retrieved)
    if coin_id:
        print(f"\n--- Testing add_snapshot for coin_id: {coin_id} ---")
        snapshot_id = add_snapshot(coin_id, 
                                   market_cap=10000.50, 
                                   reply_count_x=150, 
                                   retweet_count_x=75, 
                                   mention_count_xai=500, 
                                   pumpfun_volume_usd=5000.25, 
                                   pumpfun_market_cap_usd=9500.75)
        if snapshot_id:
            print(f"add_snapshot returned ID: {snapshot_id}")
        else:
            print(f"Failed to add snapshot for coin_id: {coin_id}")
    else:
        print("\nSkipping add_snapshot test as coin_id was not retrieved.")
        
    print("\n--- database_manager.py tests finished ---")
