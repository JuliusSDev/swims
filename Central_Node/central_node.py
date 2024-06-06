# ------------------------ INCLUDES ------------------------
import os
import sys
import logging
import socket

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from inc.custom_logger import get_custom_logger
from inc.messages import status, modes, messageID

# ------------------------ GLOBAL VARIABLES ------------------------
# Get the custom logger
logger = get_custom_logger('my_logger', level=logging.DEBUG)
newNode = 0
IPADDRESS = "192.168.211.217"
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

def create_new_csv_file(nodeID):
    logger.debug(f"Entering function create_new_csv_file()")
    file_path = f'data/node{nodeID}.csv'
    with open(file_path, mode='w', newline='') as file:
        file.write("temp, humidity, soilMoisture\n")
        file.close()

def write_data_in_csv(nodeID, temp, humidity, soilMoisture):
    logger.debug(f"Entering function create_new_csv_file()")
    file_path = f'data/node{nodeID}.csv'
    with open(file_path, mode='w', newline='') as file:
        file.write("{temp}, {humidity}, {soilMoisture}\n")
        file.close()



def handle_message_new_node(message, client_socket):
    logger.debug(f"Entering function handle_message_new_node()")
    #if (message[0] == messageID['']): # UNKNOWN NODE -> give it a new one 
    global newNode
    msg1 = f"{messageID['NEW_NODE_ACK']} {newNode}"
    logger.debug(f"Sending {msg1}")
    client_socket.send(msg1.encode("utf-8"))
    create_new_csv_file(newNode)
    newNode += 1

def handle_message_emergency():
    logger.debug(f"Entering function handle_message_emergency()")
    return

def handle_message_settings_ack():
    logger.debug(f"Entering function handle_message_settings_ack()")
    return

def handle_message_close_connection():
    logger.debug(f"Entering function handle_message_close_connection()")
    return

def handle_message_init_contact(message, client_socket):
    logger.debug(f"Entering function handle_message_init_contact()")
    nodeID = message[1]
    status = message[2]
    temp = message[3]
    soil = message[4]
    humid = message[5]
    write_data_in_csv(nodeID, temp, humid, soil)

def handle_message(message, client_socket):
    logger.debug(f"Entering function main()")
    logger.debug(f"Received following message: {message}")
    received_msgID = message[0]
    logger.debug(f"searching for following messageID: {message[0]}")
    logger.debug(f"checking for: {messageID['NEW_NODE_INIT']}")
    if(received_msgID == str(messageID["NEW_NODE_INIT"])):
        handle_message_new_node(message, client_socket)
    elif(received_msgID == str(messageID["INIT"])):
        handle_message_init_contact(message, client_socket)
    elif(received_msgID == str(messageID["EMERGENCY"])):
        handle_message_emergency()
    elif(received_msgID == str(messageID["SETTINGS_ACK"])):
        handle_message_settings_ack()
    elif(received_msgID == str(messageID["CLOSE"])):
        handle_message_close_connection()
    else:
        logger.error("Unknown Message type detected")



def main (server,):
    logger.debug(f"Entering function main()")

    stop = False
    while not stop:
        logger.debug("Accepting connection")
        client_socket, client_address = server.accept()
        #try:
        logger.info(f"Connection accepted under {client_address}")
        handle_message(client_socket.recv(1024).decode("utf-8").split(" "), client_socket)
            
            # request = client_socket.recv(1024).decode("utf-8").split(" ")
            # logger.debug(f"From {client_address} received \"NodeID:{request[0]}; temp:{request[1]}; soil:{request[2]}; humid:{request[3]}\"")
            # nodeID = request[0]
            # avrgtemp = request[1]
            # avrgsoil = request[2]
            # avrghumidity = request[3]

            # goalsoil = 70
            # wakeupInterval = 1
            # sendInterval = 10
            # mode = modes["SUMMER"]
            # msg1 = f"0x02 {nodeID} {avrgtemp} {avrgsoil} {avrghumidity} {mode} {goalsoil} {wakeupInterval} {sendInterval}"
            # client_socket.send(msg1.encode("utf-8"))

            # request = client_socket.recv(1024).decode("utf-8").split(" ")
            # logger.debug(f"From {client_address} received\"")
            # nodeID = request[0]
                
        #except:
            # logger.warning('Keyboard interrupt detected')
            # client_socket.close()
            # logger.info(f"client_socket under {client_address} closed.")
            # raise Exception(KeyboardInterrupt) 
        


        client_socket.close()
        logger.info(f"client_socket under {client_address} closed.")


# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in central_node.py")
    server = setup_server()
    # try:
    main(server)
    # except:
    #     logger.warning('Keyboard interrupt detected')

    server.close()
    logger.info(f"Server closed.")