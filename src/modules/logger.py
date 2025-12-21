import logging
import os
import traceback
from datetime import datetime

# Setup logging
LOG_FILE = "fedoraclean_debug.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w' # Overwrite each run for cleaner debug cycle, or 'a' for append
)

def log_info(msg):
    logging.info(msg)

def log_error(msg):
    logging.error(msg)
    
def log_exception(e):
    logging.error(f"Exception occurred: {str(e)}")
    logging.error(traceback.format_exc())

def get_log_path():
    return os.path.abspath(LOG_FILE)
