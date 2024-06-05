# ------------------------ INCLUDES ------------------------
import os
import sys
import logging
import socket
import time
import random
import adafruit_dht
import board
import RPi.GPIO as GPIO

# own libraries
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from inc.custom_logger import get_custom_logger
import inc.messages
from inc.messages import status, modes, messageID

# ------------------------ GLOBAL VARIABLES ------------------------
# Get the custom logger
logger = get_custom_logger('my_logger', level=logging.INFO)

# Configure DHT22 and the output for the relais(pump)
dht_22 = adafruit_dht.DHT22(board.D17) # GPIO-Pin 17 (GPIO17)
GPIO.setmode(GPIO.BCM)
PIN_RELAIS = 27
GPIO.setup(PIN_RELAIS, GPIO.OUT)

# Configure default values
mode = 0
NODEID = -1
goalSoilMoisture = 20
wakeupIntervall = 5 # Every 5 seconds
sendIntervall = 120 # every 2 minutes

server_ip = "127.0.0.1"  # replace with the server's IP address
server_port = 8000

# the arrays needed to calculate the average
temp = []
soilMoist = []
humidity = []

# ------------------------ USER FUNCTION ------------------------
def readDHT22 ():
    logger.debug(f"Entering function readDHT22()")
    try:
        temp_ = dht_22.temperature
        humid_ = dht_22.humidity
        if humid_ is not None and temp_ is not None:
            return (temp_, humid_)
        else:
            logger.error("Failed to retrieve Temp and Humidity from DHT22")
    except RuntimeError as error:
        logger.error(f"Catched RuntimeException {error.args[0]}")
    except Exception as error:
        # dht_device.exit()
        logger.error("Catched unknown exception")
    logger.error("Reached failsafe values for DHT22")
    return (-40, 0) # Failsafe if it couldn't get values

def readSoilMoisture():
    return 256

def collectData ():
    logger.debug(f"Entering function collectData()")
    (temp_, humid_) = readDHT22()
    soil_ = readSoilMoisture()
    logger.info(f"Read values with temp: {temp_}; humidity: {humid_}; soilMoisture: {soil_}")
    temp.append(temp_)
    soilMoist.append(soil_)
    humidity.append(humid_)

def pumpWater (volume):
    logger.debug(f"Entering function pumpWater()")
    timeSleep = volume / 28.5 # average flowrate of around 28.5ml/s
    # that pumping for "eternity" is not possible
    if timeSleep > wakeupIntervall:
        timeSleep = wakeupIntervall
    logger.info(f"Turning pump on for {timeSleep} seconds")
    GPIO.output(PIN_RELAIS, GPIO.LOW)
    time.sleep(timeSleep)
    GPIO.output(PIN_RELAIS, GPIO.HIGH)
    logger.debug("turning pump off")

def average(lst):
    logger.debug(f"Entering function average()")
    return sum(lst) / len(lst)


def initiate_node():
    logger.debug(f"Entering function initiate_node()")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug(f"Client socket created.")

    client.connect((server_ip, server_port))
    logger.debug(f"Client socket connected.")

    logger.info("Contact initiated with Central_Node")

    msg = "0x42"

    logger.debug(f"Send message with {msg}")
    client.send(msg.encode("utf-8")[:1024])

    answer1 = client.recv(1024).decode("utf-8")

    if(answer1[0] == "0x43"):
        global NODEID
        NODEID = answer1[1]




def sendMessage ():
    global NODEID
    logger.debug(f"Entering function sendMessage()")
    average_temp_sent = average(temp)
    average_soilMoist_sent = average(soilMoist)
    average_humidity_sent = average(humidity)
    msg = f"{messageID["INIT"]} {NODEID} {average_temp_sent} {average_soilMoist_sent} {average_humidity_sent}"
    temp.clear()
    soilMoist.clear()
    humidity.clear()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug(f"Client socket created.")

    client.connect((server_ip, server_port))
    logger.debug(f"Client socket connected.")

    logger.info("Contact initiated with Central_Node")

    logger.debug(f"Send message with {msg}")
    client.send(msg.encode("utf-8")[:1024])


    answer1 = client.recv(1024).decode("utf-8")
    logger.debug(f"Received answer with {answer1}")
    answer1 = answer1.split(" ")
    msgID1 = answer1[0]
    nodeID1 = answer1[1]
    if ((nodeID1 == NODEID) and (msgID1 == "0x02")):
        global mode,goalSoilMoisture,wakeupIntervall,sendIntervall
        average_temp_recv = answer1[2]
        average_soilMoist_recv = answer1[3]
        average_humidity_recv = answer1[4]
        mode = answer1[5]
        goalSoilMoisture = answer1[6]
        wakeupIntervall = answer1[7]
        sendIntervall = answer1[8]

        if ((average_temp_sent != int(average_temp_recv)) or (average_humidity_sent != int(average_humidity_recv)) or (average_soilMoist_sent != int(average_soilMoist_recv))):
            logger.error("received data differs from sent data")
        msg = f"0x03 {NODEID} {mode} {goalSoilMoisture} {wakeupIntervall} {sendIntervall}"
        logger.info(f"Send message with {msg}")
        client.send(msg.encode("utf-8")[:1024])



    client.close()
    logger.debug(f"Client socket closed.")

def main ():
    logger.debug(f"Entering function main()")

    lastSent = 0
    while True:
        time.sleep(wakeupIntervall)
        collectData()
        if(soilMoist[len(soilMoist-1)] < goalSoilMoisture):
            pumpWater(100)

        if lastSent+ sendIntervall < time.time():
            sendMessage()
            lastSent = time.time()







# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in plant_node.py")
    try:
        main()
    except:
        logger.warning('Keyboard interrupt detected')
    GPIO.cleanup()

