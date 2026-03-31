"""
Author: dev.slife
Date Created: 2/19/26
Date Updated: 3/31/26
Description: Holds configuration values for Pico Heat Monitor.
"""

# ------------------------- HARDWARE CONFIG ------------------------- #

CLOCK_SPEED = 1
UPDATE_THRESHOLD = 60
TEMP_OFFSET = 2
HUM_OFFSET = 8


# ------------------------- DEVICE INFO ------------------------- #

PICO_NAME = "Pico<#1>"
PICO_ROOM = "Room<#1>"


# ------------------------- PIN CONFIG ------------------------- #

BME_SDA_PIN = 4
BME_SCL_PIN = 5
OLED_SDA_PIN = 6
OLED_SCL_PIN = 7


# ------------------------- NETWORK CONFIG ------------------------- #

WIFI_SSID = ""
WIFI_PASSWORD = ""
SERVER_URL = ""
FORM_MAP = {
    "Unique ID": "",
    "Assigned Room": "",
    "Time Recorded": "",
    "Date Recorded": "",
    "Raw Temperature": "",
    "Temperature": "",
    "Raw Humidity": "",
    "Humidity": ""
}