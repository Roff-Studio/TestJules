# src/api_clients.py
import os
import requests
import json # Though requests.json() is usually sufficient

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
            raise ValueError("XAI_API_KEY not found in environment variables. "
                             "Please set it in your .env file or environment.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def fetch_twitter_trends(self, query: str, max_tokens: int = 1000) -> dict:
        """
        Fetches live trends or search results from X (Twitter) using the xAI API.

        Args:
            query: The search query string (e.g., "trending memecoins on Solana").
            max_tokens: The maximum number of tokens for the response.

        Returns:
            A dictionary containing the JSON response from the API.

        Raises:
            requests.exceptions.HTTPError: If the API returns an HTTP error status.
            requests.exceptions.RequestException: For other network or request-related issues.
        """
        endpoint = f"{self.BASE_URL}/chat/completions"
        payload = {
            "model": "grok-1",  # Using "grok-1" as specified, confirm if other models are better/cheaper
            "messages": [{"role": "user", "content": query}],
            "sources": [{"type": "x"}],  # Specify X (Twitter) as the source
            "max_tokens": max_tokens,
            "temperature": 0.7,  # A common default for creative/informative balance
            "top_p": 1,          # A common default
        }

        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            # Log or handle specific HTTP errors if needed
            print(f"HTTP error occurred: {http_err} - {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            # Log or handle other request exceptions (network issues, timeouts, etc.)
            print(f"Request exception occurred: {req_err}")
            raise
        except json.JSONDecodeError as json_err: # If response.json() fails
            print(f"JSON decode error: {json_err} - Response was: {response.text}")
            raise

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
            print("Warning: PUMPFUN_API_KEY not found in environment variables. "
                  "Some PumpFunClient functionality might be limited or require a private key.")
        # TODO: Define Pump.fun base URL when known.
        # self.headers = { # Example, if API key is used in headers
        #     "Authorization": f"Bearer {self.api_key}",
        #     "Content-Type": "application/json",
        # }

    def get_coin_data(self, token_address: str) -> dict:
        """
        Placeholder for fetching detailed data for a specific coin/token on Pump.fun.

        Args:
            token_address: The contract address of the token.

        Returns:
            An empty dictionary as a placeholder.
        """
        print(f"Placeholder: Pump.fun get_coin_data called for {token_address}. Actual API call not implemented.")
        # TODO: Implement actual API call to Pump.fun to get coin data.
        # This will require knowing the correct Pump.fun API endpoint and request/response format.
        # Error handling and data parsing will also be needed here.
        return {}

    def get_active_coins(self, limit: int = 100) -> list:
        """
        Placeholder for fetching a list of active or trending coins on Pump.fun.

        Args:
            limit: The maximum number of coins to fetch.

        Returns:
            An empty list as a placeholder.
        """
        print(f"Placeholder: Pump.fun get_active_coins called with limit {limit}. Actual API call not implemented.")
        # TODO: Implement actual API call to Pump.fun to get active coins.
        # This will require knowing the correct Pump.fun API endpoint and request/response format.
        # Error handling and data parsing will also be needed here.
        return []

if __name__ == '__main__':
    # This is a simple test and example usage.
    # Ensure your API keys are set in your .env file and python-dotenv is used to load them,
    # or that the keys are available in your environment.

    print("Attempting to load .env file for testing...")
    try:
        from dotenv import load_dotenv
        # Assuming .env is in the parent directory relative to src/api_clients.py
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            print(f".env file loaded from: {dotenv_path}")
        else:
            print(f".env file not found at: {dotenv_path}, relying on environment-set API keys.")
    except ImportError:
        print("python-dotenv not installed, relying on environment-set API keys.")
    except Exception as e:
        print(f"Error loading .env: {e}")

    print("\n--- Testing XAIClient ---")
    try:
        xai_client = XAIClient()
        print("XAIClient initialized successfully.")
        sample_query = "What are the latest trends in AI?"
        print(f"Attempting to fetch trends for query: '{sample_query}' (API call skipped)")
        # Note: Actually making a call will use your API quota.
        # trends = xai_client.fetch_twitter_trends(sample_query)
        # print("Trends received:")
        # print(json.dumps(trends, indent=2))
        print("Skipping actual xAI API call in this basic test to conserve quota.")
        print("If XAI_API_KEY was loaded and client initialized, the setup is correct.")
    except ValueError as ve:
        print(f"Error initializing XAIClient: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during XAIClient testing: {e}")

    print("\n--- Testing PumpFunClient ---")
    try:
        pump_fun_client = PumpFunClient()
        print("PumpFunClient initialized.")
        if pump_fun_client.api_key:
            print(f"Pump.fun API key loaded: {pump_fun_client.api_key[:5]}... (partially hidden)")
        else:
            print("Pump.fun API key was not found (as per warning during init).")
        
        print("Calling placeholder get_coin_data...")
        pump_fun_client.get_coin_data("SOL_TOKEN_ADDRESS_EXAMPLE")
        
        print("Calling placeholder get_active_coins...")
        pump_fun_client.get_active_coins(50)
        print("PumpFunClient placeholder methods tested.")

    except Exception as e:
        print(f"An unexpected error occurred during PumpFunClient testing: {e}")

    print("\nAPI client script execution finished.")
