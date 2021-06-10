import logging
import sys

# Log file location
logfile = 'debug.log'
# Define the log format
log_format = (
    '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

# Define basic configuration
logging.basicConfig(
    # Define logging level
    level=logging.DEBUG,
    # Declare the object we created to format the log messages
    format=log_format,
    # Declare handlers
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler(sys.stdout),
    ]
)

# Define your own logger name
log = logging.getLogger(__name__)