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
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn
import csv

# own libraries
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from inc.custom_logger import get_custom_logger
import inc.messages
from inc.messages import status, modes, messageID

# ------------------------ GLOBAL VARIABLES ------------------------
# Get the custom logger
logger = get_custom_logger('my_logger', level=logging.DEBUG)

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

server_ip = "192.168.211.217"  # replace with the server's IP address
server_port = 8000

# the arrays needed to calculate the average
temp = []
soilMoist = []
humidity = []


# # Calibration values (you need to determine these by measuring)
# DRY_VALUE = 32767  # Replace with your dry sensor value
# WET_VALUE = 0  # Replace with your wet sensor value

# # Create the I2C bus
# i2c = busio.I2C(board.SCL, board.SDA)

# # Create the ADC object using the I2C bus
# adc = Adafruit_ADS1x15.ADS1115()

# # Create single-ended input on channel 0
# chan = AnalogIn(adc, ADS.P0)

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
        logger.error(f"Catched unknown exception {error.args[0]} ")
    logger.error("Reached failsafe values for DHT22")
    return (-40, 0) # Failsafe if it couldn't get values

def readSoilMoisture():
    # # Read the analog value
    # raw_value = chan.value
    # voltage = chan.voltage
    
    # # Convert raw_value to percentage
    # if raw_value > DRY_VALUE:
    #     raw_value = DRY_VALUE
    # elif raw_value < WET_VALUE:
    #     raw_value = WET_VALUE
    
    # moisture_percentage = (1 - (raw_value - WET_VALUE) / (DRY_VALUE - WET_VALUE)) * 100
    
    # return moisture_percentage, raw_value, voltage
    return 100

def collectData ():
    logger.debug(f"Entering function collectData()")
    (temp_, humid_) = readDHT22()
    soil_ = readSoilMoisture()
    logger.info(f"Read values with temp: {temp_}; humidity: {humid_}; soilMoisture: {soil_}")
    global temp,soilMoist,humidity
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

    global server_ip, server_port
    client.connect((server_ip, server_port))
    logger.debug(f"Client socket connected.")

    logger.info("Contact initiated with Central_Node")

    global messageID
    msg = f"{messageID['NEW_NODE_INIT']}"

    logger.debug(f"Send message with {msg}")
    client.send(msg.encode("utf-8")[:1024])

    answer1 = client.recv(1024).decode("utf-8")
    logger.debug(f"Send received with {answer1}")

    if(answer1[0] == messageID['NEW_NODE_ACK']):
        global NODEID
        NODEID = answer1[1]
        logger.debug(f"NODEID changed to {answer1[1]}")




def sendMessage ():
    
    global NODEID
    logger.debug(f"Entering function sendMessage()")
    average_temp_sent = average(temp)
    average_soilMoist_sent = average(soilMoist)
    average_humidity_sent = average(humidity)
    msg = f"0x01 {NODEID} {average_temp_sent} {average_soilMoist_sent} {average_humidity_sent}"
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

def write_settings(nodeID, goalSoilMoisture):
    logger.debug(f"Entering function write_settings()")
    file_path = 'settings.csv'
    # with open(file_path, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['nodeID', 'goalSoilMoisture'])
    #     writer.writerow([nodeID, goalSoilMoisture])

def get_node_id():
    logger.debug(f"Entering function get_node_id()")
    file_path = 'settings.csv'
    # Check if the file exists
    if os.path.exists(file_path):
        logger.debug(f"Settings.csv exists")
        # Load the parameters from the file
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            settings = next(reader)
            global goalSoilMoisture, NODEID
            NODEID = settings['nodeID']
            goalSoilMoisture = float(settings['goalSoilMoisture'])
            
    else:
        logger.debug(f"Settings.csv does not exists")
        #global goalSoilMoisture, NODEID
        (NODEID, goalSoilMoisture) = initiate_node()
        write_settings(NODEID, goalSoilMoisture)


def main ():
    logger.debug(f"Entering function main()")
    global NODEID, PIN_RELAIS
    GPIO.output(PIN_RELAIS, GPIO.HIGH)

    get_node_id()
    logger.info(f"Node loaded with NODEID: {NODEID}")

    # initiate_node()


    lastSent = 0
    while True:
        collectData()
        if(soilMoist[len(soilMoist-1)] < goalSoilMoisture):
            pumpWater(100)

        if lastSent+ sendIntervall < time.time():
            # sendMessage()
            lastSent = time.time()

        time.sleep(wakeupIntervall)







# ------------------------ MAIN FUNCTION ------------------------
if __name__ == "__main__":
    logger.debug("Starting in plant_node.py")
    #try:
    main()
    #except KeyboardInterrupt:
        # logger.warning('Keyboard interrupt detected')
    #except Exception as e:
        # logger.warning(f"Unhandled Exception detected {e.args[0]}")
    GPIO.cleanup()
    logger.debug("GPIO cleaned up")

