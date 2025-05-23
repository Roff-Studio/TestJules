import os
from dotenv import load_dotenv

# Attempt to load environment variables from .env file
print("Attempting to load environment variables...")
load_dotenv()

# Example of accessing the keys (optional, for demonstration)
# xai_api_key = os.getenv("XAI_API_KEY")
# pumpfun_api_key = os.getenv("PUMPFUN_API_KEY")

# if xai_api_key and pumpfun_api_key:
#     print("Environment variables loaded successfully (example keys found).")
# else:
#     print("Environment variables not found or .env file missing.")

# The rest of your main application logic will go here.
print("Main script logic would follow here.")
