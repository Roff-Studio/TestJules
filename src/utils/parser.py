# src/utils/parser.py
import json
import re
import logging

logger = logging.getLogger(__name__)

# Regex for typical Solana addresses (base58, 32-44 characters)
# This is a general regex; specific validation might be more complex.
SOLANA_ADDRESS_REGEX = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")

def _standardize_coin_data(coin_data: dict) -> dict:
    """
    Standardizes a single coin data dictionary to a common format.
    """
    standardized = {}
    # Order of preference for keys if multiple aliases exist
    standardized['name'] = coin_data.get('name') or coin_data.get('coin_name')
    standardized['symbol'] = coin_data.get('symbol') or coin_data.get('ticker')
    standardized['token_address'] = coin_data.get('token_address') or \
                                    coin_data.get('contract_address') or \
                                    coin_data.get('address') or \
                                    coin_data.get('mint_address')
    standardized['description'] = coin_data.get('description') or \
                                  coin_data.get('text') or \
                                  coin_data.get('tweet_text') or \
                                  coin_data.get('details')
    standardized['twitter_handle'] = coin_data.get('twitter_handle') or \
                                     coin_data.get('user_handle') or \
                                     coin_data.get('twitter') or \
                                     coin_data.get('x_handle')
    
    # Remove keys with None values for cleaner output
    return {k: v for k, v in standardized.items() if v is not None}

def parse_xai_response_content(content: str | None) -> list[dict]:
    """
    Parses the string content from XAIClient.fetch_twitter_trends.
    It tries to parse as JSON first, then falls back to text-based extraction.

    Args:
        content: The string content from the xAI API response.

    Returns:
        A list of dictionaries, each representing a potential coin.
        Dictionaries may be sparsely populated if derived from text.
    """
    if not content:
        logger.info("Received None or empty content for parsing. Returning empty list.")
        return []

    parsed_coins = []

    # 1. Attempt to parse as JSON
    try:
        data = json.loads(content)
        logger.info("Content successfully parsed as JSON.")

        if isinstance(data, list): # Direct list of coin objects
            potential_coins = data
        elif isinstance(data, dict): # Dictionary that might contain a list of coins
            # Common patterns: a key like 'coins', 'results', 'data', or the top-level dict itself is a coin
            if 'coins' in data and isinstance(data['coins'], list):
                potential_coins = data['coins']
            elif 'results' in data and isinstance(data['results'], list):
                potential_coins = data['results']
            elif 'data' in data and isinstance(data['data'], list): # Check if 'data' key holds the list
                potential_coins = data['data']
            elif len(data.keys()) > 0 and all(isinstance(v, dict) for v in data.values()): # A dict of coins
                 potential_coins = list(data.values())
            elif all(k in data for k in ['name', 'symbol', 'token_address', 'description']): # Single coin object
                potential_coins = [data]
            else: # Try to see if any value in the dict is a list of coins
                potential_coins = []
                for key in data:
                    if isinstance(data[key], list):
                        potential_coins.extend(item for item in data[key] if isinstance(item, dict))
                        # Take the first list of dicts found
                        if potential_coins:
                            logger.info(f"Found list of potential coins under key '{key}'.")
                            break 
                if not potential_coins:
                    logger.warning("JSON content is a dictionary, but could not identify a list of coins. "
                                   "Attempting to treat the dictionary itself as a single coin.")
                    potential_coins = [data] # Treat the dict itself as a single coin object
        else:
            logger.warning(f"JSON content is not a list or a recognized dictionary structure. Type: {type(data)}")
            potential_coins = []

        for coin_obj in potential_coins:
            if isinstance(coin_obj, dict):
                standardized = _standardize_coin_data(coin_obj)
                if standardized.get('token_address') or standardized.get('name'): # Require at least some identifier
                    parsed_coins.append(standardized)
            else:
                logger.warning(f"Found non-dictionary item in potential coins list: {coin_obj}")
        
        logger.info(f"Found {len(parsed_coins)} potential coins from JSON content.")

    except json.JSONDecodeError:
        logger.warning("XAI content is not valid JSON. Attempting text-based extraction.")
        
        # 2. Fallback to text-based extraction (regex for Solana addresses)
        # Create a set to avoid duplicate addresses from text
        found_addresses = set()
        
        for match in SOLANA_ADDRESS_REGEX.finditer(content):
            address = match.group(0)
            if address not in found_addresses:
                # Try to get some context around the address
                start_index = max(0, match.start() - 100)
                end_index = min(len(content), match.end() + 100)
                raw_text_segment = content[start_index:end_index].strip().replace("\n", " ")
                
                coin_info = {
                    "token_address": address,
                    "raw_text": raw_text_segment,
                    "source_type": "text_extraction_solana_address"
                }
                # Very basic name/symbol extraction (example, can be improved)
                # Look for words starting with '$' or all-caps words near the address
                # This is highly heuristic and might be noisy.
                context_words = re.findall(r"[$A-Z]{2,10}", raw_text_segment[:50]) # words before address
                if context_words:
                    # Prioritize symbols like $SYMBOL
                    symbols = [w for w in context_words if w.startswith('$')]
                    if symbols:
                        coin_info['symbol_guess'] = symbols[-1] # last symbol before address
                    else: # Try all-caps words as name guess
                        coin_info['name_guess'] = ' '.join(w for w in context_words if not w.startswith('$'))


                parsed_coins.append(coin_info)
                found_addresses.add(address)
        
        logger.info(f"Found {len(parsed_coins)} potential coin mentions via text-based Solana address extraction.")

    return parsed_coins

# --- Test Block ---
if __name__ == '__main__':
    try:
        from src.utils.error_handling import setup_logging
        setup_logging() # Call the full logging setup from error_handling.py
        logger.info("Logging configured via src.utils.error_handling.setup_logging for parser tests.")
    except ImportError:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        logger.info("Basic logging configured for parser tests (src.utils.error_handling.setup_logging not found).")

    logger.info("\n--- Starting parser.py tests ---")

    # Sample 1: Valid JSON string (list of coins)
    sample_json_content_list = """
    [
        {
            "name": "TestCoin One",
            "symbol": "TC1",
            "token_address": "Addr1TC1XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "description": "First test coin from a JSON list."
        },
        {
            "coin_name": "TestCoin Two",
            "ticker": "TC2",
            "contract_address": "Addr2TC2XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "tweet_text": "Second test coin, different field names.",
            "x_handle": "@tc2dev"
        }
    ]
    """
    logger.info("\n--- Testing with valid JSON list ---")
    parsed_from_json_list = parse_xai_response_content(sample_json_content_list)
    logger.info(f"Parsed from JSON list ({len(parsed_from_json_list)} items):")
    for item in parsed_from_json_list:
        logger.info(item)

    # Sample 2: Valid JSON string (object containing a list of coins)
    sample_json_content_object = """
    {
        "status": "success",
        "data": [
            {
                "name": "AlphaCoin",
                "symbol": "ALPH",
                "mint_address": "AlphaMintXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "details": "Alpha coin from object."
            }
        ],
        "timestamp": "2024-05-21T12:00:00Z"
    }
    """
    logger.info("\n--- Testing with valid JSON object (nested list) ---")
    parsed_from_json_object = parse_xai_response_content(sample_json_content_object)
    logger.info(f"Parsed from JSON object ({len(parsed_from_json_object)} items):")
    for item in parsed_from_json_object:
        logger.info(item)

    # Sample 3: Plain text content with Solana addresses and keywords
    sample_text_content = """
    Check out this new memecoin $COOLCAT launching on Pump.fun! 
    Contract: CoolCatAddressXXXXXXXXXXXXXXXXXXXXXXXXXXXXX. It's going to the moon!
    Another one to watch is $DOGERINO, address DogeRinoAddressXXXXXXXXXXXXXXXXXXXXXXXXXXX.
    Also, someone mentioned SILLYDRAGON SillyDragonXXXXXXXXXXXXXXXXXXXXXXXXXXXXX, could be big.
    And a raw address with no ticker: SomeRandomSolanaAddressXXXXXXXXXXXXXXXXX.
    """
    logger.info("\n--- Testing with plain text content ---")
    parsed_from_text = parse_xai_response_content(sample_text_content)
    logger.info(f"Parsed from text ({len(parsed_from_text)} items):")
    for item in parsed_from_text:
        logger.info(item)

    # Sample 4: Empty content
    logger.info("\n--- Testing with empty content ---")
    parsed_empty = parse_xai_response_content("")
    logger.info(f"Parsed from empty content ({len(parsed_empty)} items): {parsed_empty}")

    # Sample 5: None content
    logger.info("\n--- Testing with None content ---")
    parsed_none = parse_xai_response_content(None)
    logger.info(f"Parsed from None content ({len(parsed_none)} items): {parsed_none}")
    
    # Sample 6: JSON that is a single object, not a list
    sample_json_single_object = """
    {
        "name": "SingleCoin",
        "symbol": "SGL",
        "token_address": "SingleCoinAddressXXXXXXXXXXXXXXXXXXXXXXXXX",
        "description": "This is a single coin object, not in a list."
    }
    """
    logger.info("\n--- Testing with valid JSON (single object) ---")
    parsed_from_json_single = parse_xai_response_content(sample_json_single_object)
    logger.info(f"Parsed from JSON single object ({len(parsed_from_json_single)} items):")
    for item in parsed_from_json_single:
        logger.info(item)

    logger.info("\n--- parser.py tests finished ---")
