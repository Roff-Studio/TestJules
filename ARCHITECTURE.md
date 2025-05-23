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
