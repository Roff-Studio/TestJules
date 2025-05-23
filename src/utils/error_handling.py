# src/utils/error_handling.py
import logging
import os
import time
import functools

# --- Logging Setup ---

LOG_DIR = "logs"

def setup_logging():
    """
    Configures the root logger for the application.
    Logs will be output to both a file (app.log) and the console.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Set root logger level

    # Prevent multiple handlers if setup_logging is called more than once
    if root_logger.hasHandlers():
        # Clear existing handlers if any (e.g., during reloads in interactive sessions)
        # For robust production, this might need more sophisticated handling
        # or ensuring setup_logging() is truly called only once.
        # root_logger.handlers.clear() 
        # For now, we assume it's called once or it's acceptable to add handlers again
        # if module reloaded. A more robust check might be a global flag.
        pass


    # File Handler
    log_file_path = os.path.join(LOG_DIR, "app.log")
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO) # File handler logs INFO and above
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Console handler also logs INFO and above (can be WARNING for less verbosity)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup complete. Logs will be written to %s", log_file_path)

# Call logging setup when the module is imported
setup_logging()

# --- Retry Decorator ---

def retry_on_error(max_retries: int = 3, delay_seconds: float = 1.0):
    """
    A decorator that retries a function call if it raises an exception.

    Args:
        max_retries: The maximum number of retry attempts.
        delay_seconds: The delay in seconds between retry attempts.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exception = None
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    last_exception = e
                    logger = logging.getLogger(func.__module__) # Get logger for the function's module
                    
                    if attempts < max_retries:
                        logger.warning(
                            "Retrying %s (attempt %d/%d) after error: %s. Waiting %.2f seconds...",
                            func.__name__, attempts, max_retries, e, delay_seconds
                        )
                        time.sleep(delay_seconds)
                    else:
                        logger.error(
                            "All %d retries for %s failed. Last error: %s",
                            max_retries, func.__name__, e
                        )
                        # No more retries, re-raise the last exception
                        # raise # This would re-raise the caught exception 'e'
            # This part is reached only if all retries failed.
            # Re-raise the last exception if it exists.
            if last_exception is not None:
                raise last_exception
            # Fallback if loop somehow finishes without an exception (should not happen with current logic)
            return None # Or raise a generic error
        return wrapper
    return decorator

# --- Test Block ---

if __name__ == '__main__':
    # Get a logger instance for this test module
    logger = logging.getLogger(__name__)

    logger.info("--- Starting error_handling.py tests ---")

    # 1. Test logging
    logger.debug("This is a debug message (should not appear with INFO level).")
    logger.info("This is an info message from the test block.")
    logger.warning("This is a warning message from the test block.")
    logger.error("This is an error message from the test block.")
    logger.critical("This is a critical message from the test block.")

    # 2. Test retry_on_error decorator
    ATTEMPT_COUNTER = 0 # Global for simplicity in test function

    @retry_on_error(max_retries=4, delay_seconds=0.5)
    def sometimes_fail_function():
        """
        A sample function that fails a few times before succeeding.
        """
        global ATTEMPT_COUNTER
        ATTEMPT_COUNTER += 1
        logger.info(f"Executing sometimes_fail_function, current attempt: {ATTEMPT_COUNTER}")
        if ATTEMPT_COUNTER < 3:
            logger.info("sometimes_fail_function will raise an error now.")
            raise ValueError(f"Simulated error on attempt {ATTEMPT_COUNTER}")
        logger.info("sometimes_fail_function executed successfully!")
        return f"Success on attempt {ATTEMPT_COUNTER}"

    @retry_on_error(max_retries=2, delay_seconds=0.2)
    def always_fail_function():
        """
        A sample function that always fails to test max retries.
        """
        logger.info("Executing always_fail_function, this will always fail.")
        raise RuntimeError("Simulated permanent failure.")

    print("\n--- Testing 'sometimes_fail_function' (should succeed after retries) ---")
    try:
        result = sometimes_fail_function()
        logger.info(f"Result from sometimes_fail_function: {result}")
    except Exception as e:
        logger.error(f"sometimes_fail_function ultimately failed after retries: {e}")

    # Reset counter for the next test if needed, or use a different function
    # ATTEMPT_COUNTER = 0 # Not strictly necessary here as 'always_fail' is different

    print("\n--- Testing 'always_fail_function' (should fail after all retries) ---")
    try:
        always_fail_function()
    except Exception as e:
        logger.error(f"always_fail_function ultimately failed as expected: {e}")

    logger.info("--- error_handling.py tests finished ---")
