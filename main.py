import os
import logging
from dotenv import load_dotenv

# Import project-specific modules
from src.utils.error_handling import setup_logging, retry_on_error
from src.api_clients import XAIClient
from src.utils.parser import parse_xai_response_content
from src.database_manager import initialize_database, add_coin, add_snapshot

# --- 1. Early Logging Setup ---
# This ensures logging is configured as soon as the script starts.
# setup_logging() should ideally handle being called multiple times gracefully or be called once.
# For this script, we assume it's the main entry point and call it here.
setup_logging()
logger = logging.getLogger(__name__) # Get a logger instance for this module

# --- 2. Environment Variable Loading ---
logger.info("Attempting to load environment variables from .env file...")
if load_dotenv():
    logger.info("Successfully loaded .env file.")
else:
    logger.warning(".env file not found or failed to load. Relying on environment-set variables if any.")
# Example: Check if a critical key is loaded
# xai_api_key_check = os.getenv("XAI_API_KEY")
# if not xai_api_key_check:
#     logger.warning("XAI_API_KEY was not found after attempting to load .env.")
# else:
#     logger.info("XAI_API_KEY found in environment.")


# --- 3. Decorated API Call Function ---
@retry_on_error(max_retries=3, delay_seconds=5)
def fetch_trends_from_xai(client: XAIClient, search_query: str) -> str | None:
    """
    Fetches trends from xAI using the provided client and query, with retry logic.
    """
    logger.info(f"Attempting to fetch trends from xAI with query: '{search_query}'")
    # Adjust max_tokens as needed; larger values might yield more comprehensive results but cost more.
    content = client.fetch_twitter_trends(search_query, max_tokens=2000)
    if content:
        logger.info("Successfully fetched and extracted content from xAI.")
        # logger.debug(f"xAI Raw Content (first 500 chars): {content[:500]}") # Log content if needed
    else:
        logger.warning("No content was returned or extracted from xAI after processing.")
    return content

# --- 4. Main Orchestration Logic ---
def run_tracker_cycle():
    """
    Runs one cycle of the tracking process:
    1. Fetches data from xAI.
    2. Parses the data.
    3. Stores relevant information in the database.
    """
    logger.info("--- Starting new tracker cycle ---")

    # Instantiate XAIClient
    try:
        xai_client = XAIClient() # This will log if API key is missing and raise ValueError
    except ValueError as e:
        logger.error(f"Failed to initialize XAIClient (likely missing API key): {e}. Aborting cycle.")
        return

    # Define the query for xAI
    # This query is designed to be specific and ask for actionable information.
    query = (
        "Identify new and trending memecoins on the Solana network. "
        "Focus on coins recently launched or gaining traction, especially on platforms like pump.fun. "
        "For each coin, if possible, provide: "
        "1. Name of the coin. "
        "2. Ticker symbol. "
        "3. Solana token contract address. "
        "4. A brief description or the tweet text discussing it. "
        "5. Any known official Twitter/X handle associated with the coin. "
        "Format the output as a JSON list of objects if possible, otherwise as clear text."
    )
    logger.debug(f"Using xAI query: {query}")

    # Fetch data from xAI (using the decorated function)
    raw_content = None
    try:
        raw_content = fetch_trends_from_xai(xai_client, query)
    except Exception as e: # Catch errors from fetch_trends_from_xai (e.g. after retries)
        logger.error(f"An error occurred during xAI data fetching: {e}", exc_info=True)
        logger.info("--- Tracker cycle finished due to xAI fetch error ---")
        return # Stop this cycle if fetching fails

    if not raw_content:
        logger.warning("No content received from xAI. Ending current cycle.")
        logger.info("--- Tracker cycle finished: No content from xAI ---")
        return

    # Parse the data
    parsed_coins = parse_xai_response_content(raw_content)
    logger.info(f"Parsed {len(parsed_coins)} potential coins from xAI response.")

    if not parsed_coins:
        logger.info("No coins were successfully parsed from the xAI response.")
        logger.info("--- Tracker cycle finished: No coins parsed ---")
        return

    # Process and store data
    coins_processed_count = 0
    coins_added_or_updated_count = 0
    snapshots_added_count = 0

    for coin_data in parsed_coins:
        coins_processed_count += 1
        token_address = coin_data.get('token_address')

        if not token_address:
            logger.warning(
                f"Skipping coin due to missing token_address. Data: {coin_data.get('name', 'Unknown Name')}, "
                f"Description: {coin_data.get('description', 'N/A')[:50]}..."
            )
            continue

        logger.info(f"Processing coin: Name='{coin_data.get('name', 'N/A')}', Symbol='{coin_data.get('symbol', 'N/A')}', Address='{token_address}'")

        # Add/update coin in DB
        db_coin_id = add_coin(
            token_address=token_address,
            name=coin_data.get('name'),
            symbol=coin_data.get('symbol'),
            source_twitter_handle=coin_data.get('twitter_handle')
            # description can be added to add_coin if schema is updated
        )

        if db_coin_id is not None: # add_coin returns ID if successful (new or existing)
            coins_added_or_updated_count += 1
            logger.info(f"Coin with address {token_address} (DB ID: {db_coin_id}) added or already exists.")

            # Add snapshot data
            # For now, 'mention_count_xai' is a simple way to note it was found.
            # Other fields like market_cap, reply_count_x would need more specific data sources or parsing.
            # The description from coin_data could be stored in a snapshot field if desired,
            # e.g. snapshot_description = coin_data.get('description')
            
            # Example of what could be passed to add_snapshot if available from xAI or other sources:
            # snapshot_market_cap = coin_data.get('market_cap_usd') 
            # snapshot_pumpfun_volume = coin_data.get('pumpfun_volume_usd')
            
            snapshot_id = add_snapshot(coin_id=db_coin_id, mention_count_xai=1) # Record that this coin was mentioned/found
            if snapshot_id:
                snapshots_added_count += 1
                logger.info(f"Snapshot (ID: {snapshot_id}) added for coin ID {db_coin_id} (Address: {token_address}).")
            else:
                logger.error(f"Failed to add snapshot for coin ID {db_coin_id} (Address: {token_address}).")
        else:
            logger.error(f"Failed to add or retrieve coin with address {token_address} from DB.")

    # Logging summary for the cycle
    logger.info("--- Tracker Cycle Summary ---")
    logger.info(f"Total items processed from xAI parse: {coins_processed_count}")
    logger.info(f"Coins added or confirmed in DB: {coins_added_or_updated_count}")
    logger.info(f"Snapshots added: {snapshots_added_count}")
    logger.info("--- Tracker cycle finished ---")


# --- 5. Script Entry Point ---
if __name__ == "__main__":
    logger.info("==================================================")
    logger.info("=== Memecoin Tracker Application - Main Start  ===")
    logger.info("==================================================")

    # Initialize the database first
    logger.info("Attempting to initialize the database...")
    try:
        initialize_database() # This function is from database_manager.py
        logger.info("Database initialization call completed successfully.")
    except Exception as e:
        logger.error(f"CRITICAL: Error initializing database from main.py: {e}", exc_info=True)
        # Depending on severity, might exit: import sys; sys.exit(1)
        logger.info("Proceeding cautiously despite database initialization error...")


    # Run the main tracking cycle
    # For now, this runs once. Future versions might loop this.
    try:
        run_tracker_cycle()
    except Exception as e:
        logger.error(f"An unexpected error occurred in the main execution block: {e}", exc_info=True)
    finally:
        logger.info("===================================================")
        logger.info("=== Memecoin Tracker Application - Main Finish  ===")
        logger.info("===================================================")
