# ------------------------ INCLUDES ------------------------
import os
import sys
import logging
import socket
import time
import random
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from inc.custom_logger import get_custom_logger
import inc.messages
from inc.messages import status, mode, messageID

# ------------------------ GLOBAL VARIABLES ------------------------
# Get the custom logger
logger = get_custom_logger('my_logger', level=logging.INFO)
mode = 0
NODEID = 42
goalSoilMoisture = 0
wakupInterval = 0.2
sendIntervall = 1
temp = []
soilMoist = []
humidity = []

# ------------------------ USER FUNCTION ------------------------
def readData ():
    logger.debug(f"Entering function readData()")
    return (random.randint(10, 30), random.randint(20, 90), random.randint(30, 90))

def collectData ():
    logger.debug(f"Entering function collectData()")
    (temp_, soil_, humid_) = readData()
    temp.append(temp_)
    soilMoist.append(soil_)
    humidity.append(humid_)

def pumpWater ():
    logger.debug(f"Entering function pumpWater()")

def average(lst): 
    logger.debug(f"Entering function average()")
    return sum(lst) / len(lst) 

def sendMessage ():
    logger.debug(f"Entering function sendMessage()")
    msg = f"{NODEID} {average(temp)} {average(soilMoist)} {average(humidity)}"
    temp.clear()
    soilMoist.clear()
    humidity.clear()
    server_ip = "127.0.0.1"  # replace with the server's IP address
    server_port = 8000 
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug(f"Client socket created.")
    client.connect((server_ip, server_port))
    logger.debug(f"Client socket connected.")
    logger.info(f"Send message with {msg}")
    client.send(msg.encode("utf-8")[:1024])
    client.close()
    logger.debug(f"Client socket closed.")

def main ():
    logger.debug(f"Entering function main()")
    
    lastSent = 0
    while True:
        time.sleep(wakupInterval)
        collectData()
        pumpWater()
        if lastSent+ sendIntervall < time.time():
            sendMessage()
            lastSent = time.time()
        #print(time.time())

        
        
    

         

# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in plant_node.py")
        #try:
    main()
    #except:
    #    logger.warning('Keyboard interrupt detected')
    