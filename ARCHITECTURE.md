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

*   **`src/api_clients.py`**: This module is responsible for all interactions with external APIs.
    *   **`XAIClient`**: A class dedicated to interfacing with the xAI Grok API. It uses the `XAI_API_KEY` from the `.env` file to authenticate requests. Its primary function is to fetch live search data and trends from X (Twitter).
    *   **`PumpFunClient`**: Currently a placeholder class, intended for future integration with the Pump.fun platform. It is expected to use the `PUMPFUN_API_KEY` (and potentially other Pump.fun related keys) for its operations, such as fetching coin data or interacting with Pump.fun services.

*   **`src/database_manager.py`**: This module centralizes all database operations, managing the SQLite database located at `data/memecoins.db`.
    *   It is responsible for the initial schema definition and any future schema evolutions.
    *   It provides a suite of functions for Create, Read, Update, and Delete (CRUD) operations on the database tables, primarily `coins` and `snapshots`.
    *   **`coins` table schema**:
        *   `id`: INTEGER, Primary Key, Auto-incrementing.
        *   `token_address`: TEXT, Unique identifier for the coin (e.g., Solana token address). Must not be NULL.
        *   `name`: TEXT, The name of the coin.
        *   `symbol`: TEXT, The symbol or ticker of the coin.
        *   `creation_timestamp`: DATETIME, The reported creation time of the coin.
        *   `source_twitter_handle`: TEXT, The Twitter handle associated with the coin, if any.
        *   `first_seen_timestamp`: DATETIME, Timestamp when the application first recorded this coin. Defaults to `CURRENT_TIMESTAMP`.
    *   **`snapshots` table schema**:
        *   `id`: INTEGER, Primary Key, Auto-incrementing.
        *   `coin_id`: INTEGER, Foreign Key referencing the `id` in the `coins` table. Must not be NULL.
        *   `timestamp`: DATETIME, Timestamp when this snapshot was taken. Defaults to `CURRENT_TIMESTAMP`.
        *   `market_cap`: REAL, Reported market capitalization at the time of snapshot.
        *   `reply_count_x`: INTEGER, Number of replies on X (Twitter) related to the coin.
        *   `retweet_count_x`: INTEGER, Number of retweets on X (Twitter).
        *   `mention_count_xai`: INTEGER, Number of mentions or relevant items found via xAI search.
        *   `pumpfun_volume_usd`: REAL, Trading volume on Pump.fun in USD.
        *   `pumpfun_market_cap_usd`: REAL, Market capitalization on Pump.fun in USD.

*   **`src/utils/error_handling.py`**: This utility module provides common error handling and logging functionalities.
    *   **`setup_logging()`**: A function that configures application-wide logging. It sets up handlers to output log messages to both a file (located in `logs/app.log`) and the console. It also ensures the `logs/` directory is created if it doesn't exist.
    *   **`@retry_on_error`**: A decorator designed to automatically retry function calls that might fail due to transient issues, such as temporary network errors during API requests. It allows configurable retry attempts and delay between retries.

*   **`src/utils/generate_pumpfun_keys.py`**: (Placeholder) This utility script is intended for future development to assist users in generating the necessary API keys and/or wallet credentials required for interacting with Pump.fun. Its full implementation is pending.

## Data Storage and Logging

*   **`data/` directory**: This directory is designated for storing persistent application data.
    *   `memecoins.db`: The SQLite database file used by `database_manager.py` to store all information about coins and their snapshots.
*   **`logs/` directory**: This directory contains application log files.
    *   `app.log`: The primary log file where operational messages, warnings, errors, and other diagnostic information are recorded by the `setup_logging()` mechanism in `error_handling.py`.

This structure helps keep data and logs organized and separate from the core application code. Both `data/` and `logs/` directories are included in `.gitignore` if they are meant for local instance data/logs not to be versioned, though `app.log` specifically is often gitignored. (Checked `.gitignore`, `data/` and `logs/` are indeed ignored).
