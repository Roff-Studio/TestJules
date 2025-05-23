# System Architecture

This document outlines the architecture of the project.

## Security and Key Management

Effective security and key management are paramount for this project due to its interaction with external APIs and potentially sensitive on-chain operations.

*   **Centralized Credential Storage:** All API keys (XAI_API_KEY, PUMPFUN_API_KEY, etc.) and other sensitive credentials are managed via the `.env` file located in the project root. This file is loaded by `main.py` at runtime using the `python-dotenv` library.

*   **Exclusion from Version Control:** The `.env` file is explicitly listed in `.gitignore` to prevent accidental leakage of sensitive credentials into the version control system (e.g., Git, GitHub). This is a critical security measure.

*   **xAI API Key (`XAI_API_KEY`):**
    *   **Generation:** This key is generated manually from the official xAI console (https://console.x.ai/).
    *   **Purpose:** This key provides authenticated access to xAI's services, such as the Grok Live Search.
    *   **Storage:** Stored as `XAI_API_KEY` in the `.env` file.

*   **Pump.fun Keys (`PUMPFUN_API_KEY`, `PUMPFUN_PRIVATE_KEY`, `PUMPFUN_PUBLIC_KEY`):**
    *   **Generation:** These keys are intended to be generated using the `src/utils/generate_pumpfun_keys.py` script. The script's goal is to provide functionality to create a new wallet (e.g., Solana keypair) and derive the necessary API credentials for interacting with Pump.fun. (The generation logic within the script is currently a work in progress and will require careful implementation and testing).
    *   **Storage:** Stored as `PUMPFUN_API_KEY`, `PUMPFUN_PRIVATE_KEY`, and `PUMPFUN_PUBLIC_KEY` in the `.env` file.
    *   **Critical Warning:** It is absolutely critical to handle the `PUMPFUN_PRIVATE_KEY` with extreme care. This key provides direct control over on-chain assets associated with the generated wallet. Exposure of the private key can lead to irreversible loss of funds.

*   **General Best Practices:**
    *   Private keys and API keys should never be hardcoded into the source code.
    *   Access to systems holding these keys (like development machines or servers) should be tightly controlled.
    *   Regularly review and consider rotating keys if supported by the services.

## System Components

This section details the core Python modules responsible for the application's functionality.

*   **`main.py` (Orchestrator)**:
    *   Serves as the main entry point and orchestrator of the application.
    *   Initializes logging, loads environment variables, and prepares the database.
    *   Implements the primary data processing cycle: fetching from xAI, parsing the response, and storing results in the database.

*   **`src/api_clients.py`**: This module is responsible for all interactions with external APIs.
    *   **`XAIClient`**: A class dedicated to interfacing with the xAI Grok API. It uses the `XAI_API_KEY` from the `.env` file to authenticate requests. Its primary function is to fetch live search data and trends from X (Twitter) as a string. It includes a helper `_extract_content_from_response` to safely get the relevant string from the API's JSON structure.
    *   **`PumpFunClient`**: Currently a placeholder class, intended for future integration with the Pump.fun platform.

*   **`src/database_manager.py`**: This module centralizes all database operations, managing the SQLite database located at `data/memecoins.db`.
    *   It is responsible for the initial schema definition and any future schema evolutions.
    *   It provides a suite of functions for Create, Read, Update, and Delete (CRUD) operations on the database tables, primarily `coins` and `snapshots`.
    *   **`coins` table schema**: `id`, `token_address` (UNIQUE), `name`, `symbol`, `creation_timestamp`, `source_twitter_handle`, `first_seen_timestamp`.
    *   **`snapshots` table schema**: `id`, `coin_id` (FK), `timestamp`, `market_cap`, `reply_count_x`, `retweet_count_x`, `mention_count_xai`, `pumpfun_volume_usd`, `pumpfun_market_cap_usd`.

*   **`src/utils/parser.py`**: This module is crucial for transforming the raw data from the xAI API into a structured and usable format.
    *   **`parse_xai_response_content(content: str | None) -> list[dict]`**: The primary function that processes the string output received from `XAIClient`.
        *   It first attempts to parse the `content` as JSON. If successful, it navigates common JSON structures (direct lists of objects, or dictionaries containing lists under keys like 'coins', 'data', 'results') to extract coin-related information.
        *   If JSON parsing fails or the content is not JSON, it falls back to text-based extraction. This involves using regular expressions (specifically `SOLANA_ADDRESS_REGEX`) to identify potential Solana token addresses. It also applies basic heuristics to guess coin names or symbols based on context words near the found addresses.
        *   Each extracted piece of information (whether from JSON or text) is standardized.
    *   **`_standardize_coin_data(coin_data: dict) -> dict`**: An internal helper function used by `parse_xai_response_content`. It maps various possible input field names (e.g., `contract_address`, `coin_name`, `ticker`, `tweet_text`) to a consistent set of output keys (`token_address`, `name`, `symbol`, `description`, `twitter_handle`). This ensures data consistency before database insertion.
    *   This module is critical for converting potentially unstructured or variably structured API responses into a list of standardized dictionaries, ready for the database.

*   **`src/utils/error_handling.py`**: This utility module provides common error handling and logging functionalities.
    *   **`setup_logging()`**: A function that configures application-wide logging. It sets up handlers to output log messages to both a file (located in `logs/app.log`) and the console. It also ensures the `logs/` directory is created if it doesn't exist.
    *   **`@retry_on_error`**: A decorator designed to automatically retry function calls that might fail due to transient issues, such as temporary network errors during API requests. It allows configurable retry attempts and delay between retries. It is notably used for the xAI API calls in `main.py`.

*   **`src/utils/generate_pumpfun_keys.py`**: (Placeholder) This utility script is intended for future development to assist users in generating the necessary API keys and/or wallet credentials required for interacting with Pump.fun.

## Data Flow

The application follows a defined pipeline to process information:

1.  **Orchestration (`main.py`)**:
    *   The process begins in `main.py`, which acts as the central orchestrator.
    *   It initializes logging (`src.utils.error_handling.setup_logging()`), loads environment variables from `.env`, and ensures the database schema is set up (`src.database_manager.initialize_database()`).

2.  **Data Ingestion (`src/api_clients.py`)**:
    *   `main.py` instantiates `XAIClient` from `src.api_clients.py`.
    *   The `XAIClient.fetch_twitter_trends()` method is called with a specific query. This method interacts with the xAI API to fetch raw data, which is returned as a string. This call is wrapped with the `@retry_on_error` decorator from `src.utils.error_handling.py` to handle transient API issues.

3.  **Data Structuring (`src/utils/parser.py`)**:
    *   The raw string content from `XAIClient` is passed to `parse_xai_response_content()` in `src.utils.parser.py`.
    *   This function attempts to parse the string as JSON. If successful, it extracts coin data and standardizes field names using `_standardize_coin_data()`.
    *   If the content is not valid JSON, it falls back to regex-based text analysis to find potential Solana addresses and associated context.
    *   The output is a list of standardized dictionaries, where each dictionary represents a potential memecoin.

4.  **Data Persistence (`src/database_manager.py`)**:
    *   `main.py` iterates through the list of structured coin dictionaries received from the parser.
    *   For each coin:
        *   `src.database_manager.add_coin()` is called to insert or update the coin's primary information in the `coins` table of `memecoins.db`.
        *   `src.database_manager.add_snapshot()` is called to record a new entry in the `snapshots` table, linking to the coin and noting its discovery (e.g., via `mention_count_xai`).

5.  **Logging and Error Handling (`src.utils.error_handling.py`)**:
    *   Throughout all stages, logging is performed using the centralized logging setup.
    *   The retry decorator provides resilience for API calls.
    *   `main.py` includes try-except blocks for robust error management during the cycle.

Currently, this entire data flow is executed once when `main.py` is run.

## Data Storage and Logging

*   **`data/` directory**: This directory is designated for storing persistent application data.
    *   `memecoins.db`: The SQLite database file used by `database_manager.py` to store all information about coins and their snapshots.
*   **`logs/` directory**: This directory contains application log files.
    *   `app.log`: The primary log file where operational messages, warnings, errors, and other diagnostic information are recorded by the `setup_logging()` mechanism in `error_handling.py`.

This structure helps keep data and logs organized and separate from the core application code. Both `data/` and `logs/` directories are included in `.gitignore`.
