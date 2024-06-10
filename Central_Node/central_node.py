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

def write_data_in_csv(nodeID, temp_, humidity, soilMoisture):
    logger.debug(f"Entering function create_new_csv_file()")
    file_path = f'data/node{nodeID}.csv'
    header_needed = False
    with open(file_path, mode='a', newline='') as file:
        file.close()
    with open(file_path, mode='r', newline='') as file:
        header = file.readline()
        logger.debug(f"Checking if Header is there or not: {header} and temp, humidity, soilMoisture\n")
        if header != "temp, humidity, soilMoisture\n":
            logger.debug("Header needed")
            header_needed = True
        file.close()

    with open(file_path, mode='a', newline='') as file:
        if header_needed:
            file.write("temp, humidity, soilMoisture\n")
        file.write(f"{temp_}, {humidity}, {soilMoisture}\n")
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

def getSettings(nodeID):
    logger.debug(f"Entering function getSettings()")
    file_path = f'settings.csv'
    with open(file_path, mode='r', newline='') as file:
        i = 0
        for lines in file:
            logger.debug(f"lines: {lines}; i: {i}; nodeID: {nodeID}")
            logger.debug(f"checking for: i: {i-1} and nodeID: {nodeID}")
            if int(nodeID) == int(i-1):
                lines = lines.split(", ")
                logger.debug(f"Lines: {lines}; lines[0]: {lines[0]}; lines[1]: {lines[1]}; lines[2]: {lines[2]};")
                goalSoilMoisture = lines[0]
                wakeUpIntervall = lines[1]
                sendIntervall = lines[2]
                return (goalSoilMoisture, wakeUpIntervall, sendIntervall)
            i += 1  

        file.close()
    return (30,2,10)

def handle_message_init_contact(message, client_socket):
    logger.debug(f"Entering function handle_message_init_contact()")
    nodeID = message[1]
    status = message[2]
    temp = message[3]
    soil = message[4]
    humid = message[5]
    (goalSoilMoisture, wakeUpIntervall, sendIntervall) = getSettings(nodeID)
    write_data_in_csv(nodeID, temp, humid, soil)
    msg = f"{messageID['INIT_ACK_AND_SEND_SETTINGS']} {nodeID} {modes['SUMMER']} {goalSoilMoisture} {wakeUpIntervall} {sendIntervall}"
    logger.debug(f"Answer with message {msg}")
    client_socket.send(msg.encode("utf-8"))

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

    while True:
        logger.debug("Accepting connection")
        client_socket, client_address = server.accept()

        logger.info(f"Connection accepted under {client_address}")
        handle_message(client_socket.recv(1024).decode("utf-8").split(" "), client_socket)

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