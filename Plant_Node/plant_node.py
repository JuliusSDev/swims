# ------------------------ INCLUDES ------------------------
import os
import sys
import logging
import socket

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from inc.custom_logger import get_custom_logger
import inc.messages

# ------------------------ GLOBAL VARIABLES ------------------------
# Get the custom logger
logger = get_custom_logger('my_logger', level=logging.DEBUG)

# ------------------------ USER FUNCTION ------------------------
def main (client):
    logger.debug(f"Entering function main()")
    
    server_ip = "127.0.0.1"  # replace with the server's IP address
    server_port = 8000 
    client.connect((server_ip, server_port))
    stop = False
    #while not stop:

         

# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in plant_node.py")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        main(client)
    except:
        logger.warning('Keyboard interrupt detected')
    client.close()
    logger.info(f"Client socket closed.")