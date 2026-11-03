"""
Author: dev.slife
Contributors: Chris Hawley
Date Created: 2/18/26
Date Updated: 11/3/26
Description: Monitors the Temperature and Humidity Levels of a room.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import machine
from modules.ntptime import *
from modules.picodata import *
from modules.piconet import http_send, connect_wifi, has_wifi
from modules.errlog import log_error
from modules.config import (
    CLOCK_SPEED,
    UPDATE_THRESHOLD,
    WIFI_DELAY,
    PICO_NAME,
    PICO_ROOM,
    BME_SDA_PIN,
    BME_SCL_PIN,
    OLED_SDA_PIN,
    OLED_SCL_PIN,
    TEMP_OFFSET,
    HUM_OFFSET
)
import time
import modules.BME280 as BME280
from modules.ssd1306 import SSD1306_I2C


# ---------------------- INITIALIZATION ---------------------- #

# I2C communication.
I2C_SENSOR = machine.I2C(0, sda=machine.Pin(BME_SDA_PIN), scl=machine.Pin(BME_SCL_PIN), freq=400000)
# I2C1 for OLED on GP6/GP7
I2C_OLED = machine.I2C(1, sda=machine.Pin(OLED_SDA_PIN), scl=machine.Pin(OLED_SCL_PIN), freq=400000)

# OLED 128x32 init on I2C1
WIDTH = 128
HEIGHT = 32
OLED = SSD1306_I2C(WIDTH, HEIGHT, I2C_OLED)

# BME280 sensor
BME = BME280.BME280(i2c=I2C_SENSOR)

# Restart the Pico if no data has been recorded to the form for this many hours
RESET_THRESHOLD = 36



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
    
    dateRecorded = data["Date Recorded"]
    
    if (dateRecorded):
        dateSplit = dateRecorded.split("-")
        Y = dateSplit[0]
        M = dateSplit[1]
        D = dateSplit[2]      
        dateRecorded = f"{M}/{D}/{Y}"
    else:
        dateRecorded = "Unknown"

    buffer = [
        # f"F: {data["Temperature"]} H: {data["Humidity"]}%",
        f"Date: {dateRecorded}",
        f"Time: {curTime if (curTime) else "Unknown"}"
    ]

    for i in range(len(buffer)):
        line = buffer[i]
        OLED.text(line, 0, 12*i)

    # show on screen
    OLED.show()



# ------------------ READING + FORMATTING DATA ------------------ #

def build_data(curDate, curTime) -> OrderedDict:
    """
    Builds a row of data from the temperature sensor.
    
    Args:
        curDate (str) - the current date given
        curTime (str) - the current time given
    
    Returns:
        A dictionary containing the following:
        - unique id of the Raspberry Pi Pico
        - time recorded (str)
        - date recorded (str)
        - hour recorded (str)
        - minute recorded (str)
        - day recorded (str)
        - year recorded (str)
        - month recorded (str)
        - temperature in Fahrenheit (float)
        - calibrated temperature in Fahrenheit (float)
        - humidity level (float)
        - calibrated humidity level (float)
        - the room number the Pico is assigned in
    """
    # Date & Time
    curTimeSplit = curTime.split(":") if (curTime) else ["Unknown", "Unknown"]
    curDateSplit = curDate.split("-") if (curDate) else ["Unknown", "Unknown", "Unknown"]
    curHour = curTimeSplit[0]
    curMin = curTimeSplit[1]
    curYear = curDateSplit[0]
    curMon = curDateSplit[1]
    curDay = curDateSplit[2]
    
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
        ("Hour Recorded", curHour),
        ("Minute Recorded", curMin),
        ("Year Recorded", curYear),
        ("Month Recorded", curMon),
        ("Day Recorded", curDay),
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
def monitor(clock=None, count=UPDATE_THRESHOLD):
    if clock is None:
        clock = piClock()
    lastSuccess = time.ticks_ms()
    while True:
        # restart if unable to connect to wifi or record data for too long
        if (time.ticks_diff(time.ticks_ms(), lastSuccess) >= RESET_THRESHOLD * 3600 * 1000):
            log_error(f"No data recorded in {RESET_THRESHOLD} hours, restarting...")
            machine.reset()
        try:
            if (not has_wifi() and count >= (WIFI_DELAY * 60)):
                count = 0
                connect_wifi()
                if (has_wifi()): clock.trySync()
            # retry the clock sync once per reading if it failed on boot or after a reconnect
            if (has_wifi() and not clock.synced and count % UPDATE_THRESHOLD == 0):
                clock.trySync()
            if (count % UPDATE_THRESHOLD == 0):
                # only reset count if there is a wifi connection
                if (has_wifi()): count = 0
                reading = build_data(clock.date, clock.time)
                display(reading)
                print("---------------------------------")
                if (clock.isTimeToReport()):
                    csv_append(reading)
                    serializedData = serializeCSV()
                    linesToRemove = []
                    if (serializedData):
                        for i in range(len(serializedData)):
                            payload = serializedData[i]
                            # the last row is the reading just taken; older rows are queued
                            # and need the time they were recorded sent with them
                            isQueued = (i < len(serializedData) - 1)
                            # successful POSTS means we can remove local data
                            if http_send(payload[0], include_time=isQueued):
                                linesToRemove.append(payload[1])
                                lastSuccess = time.ticks_ms()
                            else:
                                # keep the rest queued for the next report rather than
                                # spending every attempt on a connection that is failing
                                break
                        if (linesToRemove):
                            csv_remove(tuple(linesToRemove))
            show_screen(reading, clock.time)
            count += CLOCK_SPEED
            time.sleep(CLOCK_SPEED)
        except Exception as e:
            log_error(f"A(n) {type(e).__name__} has occurred: {e}.")
            time.sleep(WIFI_DELAY * 60)


def screenLog(text):
    OLED.fill(0)
    OLED.text(text,0,0,1)
    OLED.show()
    time.sleep(2)
    OLED.fill(0)

  


def boot_reason() -> str:
    """Names the cause of the last reset, e.g. power on or watchdog."""
    cause = machine.reset_cause()
    for name in ("PWRON_RESET", "HARD_RESET", "WDT_RESET", "DEEPSLEEP_RESET", "SOFT_RESET"):
        if (cause == getattr(machine, name, None)):
            return name
    return str(cause)


def main():
    print('main')
    # the clock isn't synced yet, so this entry is timestamped from the RTC's default date
    log_error(f"Booted, reset cause: {boot_reason()}")
    screenLog("Connecting\nto wifi")
    connect_wifi()
    screenLog(f"wifi = {has_wifi()}")
    print(f"wifi = {has_wifi()}")
    clock=piClock()
    screenLog(f"time is {clock.time}")
    monitor(clock)

if __name__ == "__main__":
    main()