# src/api_clients.py
import os
import requests
import json # Though requests.json() is usually sufficient
import logging # Added logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

class XAIClient:
    """
    A client for interacting with the xAI API.
    """
    BASE_URL = "https://api.x.ai/v1"

    def __init__(self):
        """
        Initializes the XAIClient.

        Loads the XAI_API_KEY from environment variables and sets up the base URL.
        Raises:
            ValueError: If the XAI_API_KEY is not found in the environment variables.
        """
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            logger.error("XAI_API_KEY not found in environment variables.")
            raise ValueError("XAI_API_KEY not found in environment variables. "
                             "Please set it in your .env file or environment.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        logger.info("XAIClient initialized successfully.")

    def _extract_content_from_response(self, response_json: dict) -> str | None:
        """
        Safely extracts the main message content from the xAI API JSON response.

        Args:
            response_json: The full JSON dictionary from the API.

        Returns:
            The extracted content string, or None if not found.
        """
        try:
            if not response_json:
                logger.warning("Attempted to extract content from an empty or None JSON response.")
                return None

            choices = response_json.get('choices')
            if not choices or not isinstance(choices, list) or len(choices) == 0:
                logger.warning("Unexpected xAI response structure: 'choices' is missing, not a list, or empty.")
                return None

            message = choices[0].get('message')
            if not message or not isinstance(message, dict):
                logger.warning("Unexpected xAI response structure: 'message' is missing or not a dict in the first choice.")
                return None

            content = message.get('content')
            if content is None: # Allow empty string, but not None
                logger.warning("Unexpected xAI response structure: 'content' is missing in the message.")
                return None
            
            if not isinstance(content, str):
                logger.warning(f"Expected content to be a string, but got {type(content)}. Value: {content}")
                # Optionally, try to convert to string, e.g., str(content), if that's a desired fallback
                return str(content) # Or return None if strict type checking is required

            logger.debug("Successfully extracted content from xAI response.")
            return content

        except Exception as e: # Catch any other unexpected errors during extraction
            logger.error(f"Error extracting content from xAI response: {e}", exc_info=True)
            return None

    def fetch_twitter_trends(self, query: str, max_tokens: int = 1000) -> str | None:
        """
        Fetches live trends or search results from X (Twitter) using the xAI API.

        Args:
            query: The search query string (e.g., "trending memecoins on Solana").
            max_tokens: The maximum number of tokens for the response.

        Returns:
            A string containing the extracted content from the API response, or None if extraction fails or an error occurs.

        Raises:
            requests.exceptions.HTTPError: If the API returns an HTTP error status.
            requests.exceptions.RequestException: For other network or request-related issues.
        """
        endpoint = f"{self.BASE_URL}/chat/completions"
        payload = {
            "model": "grok-1",
            "messages": [{"role": "user", "content": query}],
            "sources": [{"type": "x"}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 1,
        }
        logger.info(f"Fetching Twitter trends from xAI with query: '{query}'")

        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            logger.debug(f"Received xAI API response: {response_data}") # Log raw response for debugging
            
            return self._extract_content_from_response(response_data)

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching trends: {http_err} - {response.text}", exc_info=True)
            raise
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request exception occurred while fetching trends: {req_err}", exc_info=True)
            raise
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decode error while fetching trends: {json_err} - Response was: {response.text}", exc_info=True)
            raise # Re-raise so it's not silently None

class PumpFunClient:
    """
    A client for interacting with the Pump.fun API (placeholder).
    """
    # TODO: Define Pump.fun base URL when known.
    # PUMPFUN_BASE_URL = "https://api.pump.fun/v1" # Example

    def __init__(self):
        """
        Initializes the PumpFunClient.

        Loads the PUMPFUN_API_KEY from environment variables.
        Prints a warning if the key is not found.
        """
        self.api_key = os.getenv("PUMPFUN_API_KEY")
        if not self.api_key:
            logger.warning("PUMPFUN_API_KEY not found in environment variables. "
                           "Some PumpFunClient functionality might be limited or require a private key.")
        # TODO: Define Pump.fun base URL when known.
        # self.headers = { # Example, if API key is used in headers
        #     "Authorization": f"Bearer {self.api_key}",
        #     "Content-Type": "application/json",
        # }
        logger.info("PumpFunClient initialized.")


    def get_coin_data(self, token_address: str) -> dict:
        """
        Placeholder for fetching detailed data for a specific coin/token on Pump.fun.

        Args:
            token_address: The contract address of the token.

        Returns:
            An empty dictionary as a placeholder.
        """
        logger.info(f"Placeholder: Pump.fun get_coin_data called for {token_address}. Actual API call not implemented.")
        # TODO: Implement actual API call to Pump.fun to get coin data.
        return {}

    def get_active_coins(self, limit: int = 100) -> list:
        """
        Placeholder for fetching a list of active or trending coins on Pump.fun.

        Args:
            limit: The maximum number of coins to fetch.

        Returns:
            An empty list as a placeholder.
        """
        logger.info(f"Placeholder: Pump.fun get_active_coins called with limit {limit}. Actual API call not implemented.")
        # TODO: Implement actual API call to Pump.fun to get active coins.
        return []

if __name__ == '__main__':
    # Setup logging for testing this module directly
    # This ensures logs from this module are visible when run as a script
    try:
        from src.utils.error_handling import setup_logging
        setup_logging() # Call the full logging setup from error_handling.py
        logger.info("Logging configured via src.utils.error_handling.setup_logging for __main__ tests.")
    except ImportError:
        # Basic logging config if full setup is not available (e.g. module run in isolation)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        logger.info("Basic logging configured for __main__ tests (src.utils.error_handling.setup_logging not found).")


    print("Attempting to load .env file for testing...")
    logger.info("Attempting to load .env file for testing...") # Using logger
    try:
        from dotenv import load_dotenv
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            logger.info(f".env file loaded from: {dotenv_path}")
        else:
            logger.warning(f".env file not found at: {dotenv_path}, relying on environment-set API keys.")
    except ImportError:
        logger.warning("python-dotenv not installed, relying on environment-set API keys.")
    except Exception as e:
        logger.error(f"Error loading .env: {e}", exc_info=True)

    print("\n--- Testing XAIClient ---")
    logger.info("--- Testing XAIClient ---")
    try:
        xai_client = XAIClient() # Initialization logs XAI_API_KEY presence
        sample_query = "test query for xAI" # Simple query
        logger.info(f"Attempting to fetch trends for query: '{sample_query}' (API call skipped in test)")
        
        # --- Mocking API call for testing content extraction ---
        # This simulates a successful API call without actual network request
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": "This is a mock response content from xAI."
                    }
                }
            ]
        }
        # Directly test the _extract_content_from_response method
        logger.info("Testing _extract_content_from_response with mock data...")
        extracted_content = xai_client._extract_content_from_response(mock_response_data)
        if extracted_content:
            print("\n--- XAI Client Mock Test Response Content ---")
            logger.info(f"Successfully extracted content from mock: {extracted_content[:500]}...")
        else:
            print("\n--- XAI Client Mock Test Response ---")
            logger.warning("Failed to extract content from mock data.")

        # Test with unexpected structure
        mock_bad_response_data = {"error": "something went wrong"}
        logger.info("Testing _extract_content_from_response with bad mock data...")
        extracted_content_bad = xai_client._extract_content_from_response(mock_bad_response_data)
        if extracted_content_bad is None:
            logger.info("Correctly returned None for bad mock data structure.")
        else:
            logger.error(f"Incorrectly extracted content from bad mock data: {extracted_content_bad}")


        # The actual call to `fetch_twitter_trends` is skipped to conserve quota
        print("\nSkipping actual xAI API call in this basic test to conserve quota.")
        logger.info("Skipping actual xAI API call in `fetch_twitter_trends` to conserve quota.")
        # trends_content = xai_client.fetch_twitter_trends(sample_query, max_tokens=10)
        # if trends_content:
        #     print("\n--- XAI Client Test Response Content (Actual Call Skipped) ---")
        #     logger.info(f"Fetched content (first 500 chars): {trends_content[:500]}...")
        # else:
        #     print("\n--- XAI Client Test Response (Actual Call Skipped) ---")
        #     logger.warning("No content extracted or API call skipped/failed.")

    except ValueError as ve: # Specifically for API key not found
        print(f"Error initializing XAIClient: {ve}") # Print to console for immediate visibility
        logger.error(f"Error initializing XAIClient: {ve}", exc_info=True)
    except Exception as e:
        print(f"An unexpected error occurred during XAIClient testing: {e}")
        logger.error(f"An unexpected error occurred during XAIClient testing: {e}", exc_info=True)

    print("\n--- Testing PumpFunClient ---")
    logger.info("--- Testing PumpFunClient ---")
    try:
        pump_fun_client = PumpFunClient()
        if pump_fun_client.api_key:
            logger.info(f"Pump.fun API key loaded: {pump_fun_client.api_key[:5]}... (partially hidden)")
        
        logger.info("Calling placeholder get_coin_data...")
        pump_fun_client.get_coin_data("SOL_TOKEN_ADDRESS_EXAMPLE")
        
        logger.info("Calling placeholder get_active_coins...")
        pump_fun_client.get_active_coins(50)
        logger.info("PumpFunClient placeholder methods tested.")

    except Exception as e:
        print(f"An unexpected error occurred during PumpFunClient testing: {e}")
        logger.error(f"An unexpected error occurred during PumpFunClient testing: {e}", exc_info=True)

    print("\nAPI client script execution finished.")
    logger.info("API client script execution finished.")
