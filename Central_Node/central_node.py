# ------------------------ INCLUDES ------------------------
import os
import sys
import logging
import socket

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from inc.custom_logger import get_custom_logger

# ------------------------ GLOBAL VARIABLES ------------------------
# Get the custom logger
logger = get_custom_logger('my_logger', level=logging.DEBUG)

IPADDRESS = "192.168.0.1"
PORT = 666

# ------------------------ USER FUNCTION ------------------------
def test(i):
    logger.debug(f"Entering test() {i}")
    for a in IPADDRESS:
        logger.debug(f"a: {a}")
        

# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in central_node.py")
    for i in range(1000000):
        test(i)
    