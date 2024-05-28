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

IPADDRESS = "127.0.0.1"
PORT = 8000

# ------------------------ USER FUNCTION ------------------------
def setup_server():
    logger.debug(f"Entering function setup_server()")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IPADDRESS,PORT))
    server.listen(0)
    logger.info(f"Server setup under {IPADDRESS}:{PORT}")
    logger.debug(f"Leaving function setup_server() with returning \"server\"")
    return server


def main (server,):
    logger.debug(f"Entering function main()")

    stop = False
    while not stop:
        client_socket, client_address = server.accept()
        logger.info(f"Connection accepted under {client_address}")
        client_socket.close()


# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in central_node.py")
    server = setup_server()
    try:
        main(server)
    except:
        logger.warning('Keyboard interrupt detected')

    server.close()
    logger.info(f"Server closed.")