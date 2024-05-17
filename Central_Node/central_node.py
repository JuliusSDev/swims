# ------------------------ INCLUDES ------------------------
import os
import sys
import logging

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from inc.custom_logger import get_custom_logger

# ------------------------ GLOBAL VARIABLES ------------------------
# Get the custom logger
logger = get_custom_logger('my_logger', level=logging.DEBUG)

# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in central_node.py")
    