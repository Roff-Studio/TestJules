import os
from dotenv import load_dotenv
from src.database_manager import initialize_database # Added import

# Attempt to load environment variables from .env file
print("Attempting to load environment variables...")
load_dotenv()
print("Environment variable loading process complete.") # Added for clarity

# Example of accessing the keys (optional, for demonstration)
# xai_api_key = os.getenv("XAI_API_KEY")
# pumpfun_api_key = os.getenv("PUMPFUN_API_KEY")

# if xai_api_key and pumpfun_api_key:
#     print("Environment variables loaded successfully (example keys found).")
# else:
#     print("Environment variables not found or .env file missing.")

# Initialize the database
print("\nAttempting to initialize the database...")
try:
    initialize_database() # Call the imported function
    print("Database initialization call completed.") # Message from main.py
except Exception as e:
    print(f"Error initializing database from main.py: {e}")
    # Potentially exit or handle critical failure, e.g., sys.exit(1)

# The rest of your main application logic will go here.
print("\nMain script logic would follow here.")
