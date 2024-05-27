import logging
import os

from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv(override=True)


# Fetch environment variables.
LOG_FILEPATH = os.environ.get("LOG_FILEPATH")
if not LOG_FILEPATH:
    raise OSError("LOG_FILEPATH environment variable not set.")


# Create a formatter to define the log format
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_formatter = logging.Formatter("%(levelname)s - %(message)s")

# Create a file handler to write logs to a file
file_handler = logging.FileHandler(LOG_FILEPATH)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

# Create a stream handler to print logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(
    logging.INFO
)  # You can set the desired log level for console output
console_handler.setFormatter(console_formatter)

logger = logging.getLogger("geo_simulations")
logger.setLevel(logging.DEBUG)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

log = logging.getLogger("geo_simulations")

if __name__ == "__main__":
    logging.debug("This is a default debug message")
    logging.info("This is an default info message")
    logging.warning("This is a default warning message")
    logging.error("This is an default error message")

    log.debug("This is a custom debug message")
    log.info("This is an custom info message")
    log.warning("This is a custom warning message")
    log.error("This is an custom error message")
