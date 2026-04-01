"""
Author: dev.slife
Date Created: 2/18/26
Date Updated: 4/1/26
Description: Monitors the Temperature and Humidity Levels of a room.
"""


# ---------------------- IMPORT MODULES ---------------------- #

from machine import Pin, I2C
from modules.picotime import *
from modules.picodata import *
from modules.piconet import http_send, connect_wifi, has_wifi
from modules.config import \
    CLOCK_SPEED, \
    UPDATE_THRESHOLD, \
    WIFI_DELAY, \
    PICO_NAME, \
    PICO_ROOM, \
    BME_SDA_PIN, \
    BME_SCL_PIN, \
    OLED_SDA_PIN, \
    OLED_SCL_PIN, \
    TEMP_OFFSET, \
    HUM_OFFSET
from time import sleep
import modules.BME280 as BME280
from modules.ssd1306 import SSD1306_I2C


# ---------------------- INITIALIZATION ---------------------- #

# I2C communication.
I2C_SENSOR = I2C(0, sda=Pin(BME_SDA_PIN), scl=Pin(BME_SCL_PIN), freq=400000)
# I2C1 for OLED on GP6/GP7
I2C_OLED = I2C(1, sda=Pin(OLED_SDA_PIN), scl=Pin(OLED_SCL_PIN), freq=400000)

# OLED 128x32 init on I2C1
WIDTH = 128
HEIGHT = 32
OLED = SSD1306_I2C(WIDTH, HEIGHT, I2C_OLED)

# BME280 sensor
BME = BME280.BME280(i2c=I2C_SENSOR)



# ----------------------- CONVERSIONS ----------------------- #

def C_to_F(temp: float) -> float:
    """
    Converts a temperature from Celsius to Fahrenheit
    
    Args:
        temp (float) - the temperature in celsius
        
    Returns:
        A float representing the temperature in Fahrenheit
    """
    tempF = temp * (9/5) + 32
    tempF = round(tempF, 1)
    return tempF



# ----------------------- OLED SCREEN ----------------------- #

def show_screen(data: OrderedDict, curTime: str):
    """
    Displays temperature and humidity information on an OLED screen.
    
    Args:
        data (OrderedDict) - The data to display
        curTime (str) - The current local time (this is more up to date)
    """
    # clear screen
    OLED.fill(0)

    buffer = [
        f"F: {data["Temperature"]} H: {data["Humidity"]}%",
        f"Date: {format_MMDDYY(date=data["Date Recorded"])}",
        f"Time: {curTime}"
    ]

    for i in range(len(buffer)):
        line = buffer[i]
        OLED.text(line, 0, 12*i)

    # show on screen
    OLED.show()



# ------------------ READING + FORMATTING DATA ------------------ #

def build_data() -> OrderedDict:
    """
    Builds a row of data from the temperature sensor.
    
    Returns:
        A dictionary containing the following:
        - unique id of the Raspberry Pi Pico
        - time recorded (str)
        - date recorded (str)
        - temperature in Fahrenheit (float)
        - calibrated temperature in Fahrenheit (float)
        - humidity level (float)
        - calibrated humidity level (float)
        - the room number the Pico is assigned in
    """
    # Date & Time
    curTime, curDate = get_time(), get_date()
    
    # Temperature & Humidity
    tempC = BME.read_temperature() / 100
    tempRaw = C_to_F(tempC)
    temp = C_to_F(tempC + TEMP_OFFSET)
    humRaw = round(BME.read_humidity() / 1024)
    hum = humRaw + HUM_OFFSET
    
    return OrderedDict([
        ("Unique ID", PICO_NAME),
        ("Assigned Room", PICO_ROOM),
        ("Time Recorded", curTime),
        ("Date Recorded", curDate),
        ("Raw Temperature", tempRaw),
        ("Temperature", temp),
        ("Raw Humidity", humRaw),
        ("Humidity", hum)
    ])



# -------------------- PRINTING TO TERMINAL -------------------- #

def display(data: dict):
    """
    Displays the data on the terminal.
    
    Args:
        data (dict) - The data to display
    """
    i = 0
    result = "CURRENT READING\n"
    for dataType, dataValue in data.items():
        result += dataType + ": " + str(dataValue)
        if (i != len(data) - 1):
            result += "\n"
    print(result)
        


# ------------------------- MAIN CODE ------------------------- #

def main():
    connect_wifi()
    count = UPDATE_THRESHOLD
    while True:
        try:
            if not has_wifi() and count >= (WIFI_DELAY * 60):
                connect_wifi()
            if count >= UPDATE_THRESHOLD:
                count = 0
                reading = build_data()
                curTime = reading["Time Recorded"]
                display(reading)
                print("---------------------------------")
                csv_append(reading)
                serializedData = serializeCSV()
                linesToRemove = []
                if (serializedData):
                    for payload in serializedData:
                        # successful POSTS means we can remove local data
                        if http_send(payload[0]): linesToRemove.append(payload[1])
                    if (linesToRemove):
                        csv_remove(tuple(linesToRemove))
            show_screen(reading, curTime)
            curTime = local_inc_time(curTime, 's', CLOCK_SPEED) or curTime
            count += CLOCK_SPEED
            sleep(CLOCK_SPEED)
        except Exception as e:
            print(f"A(n) {type(e).__name__} has occurred: {e}")
    

if __name__ == "__main__":
    main()