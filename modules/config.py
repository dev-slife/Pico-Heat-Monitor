"""
Author: dev.slife
Date Created: 2/19/26
Date Updated: 10/1/26
Description: Holds configuration values for Pico Heat Monitor.
"""

# ------------------------- IMPORT MODULES ------------------------- #

import confsec



# ------------------------- HARDWARE CONFIG ------------------------- #

CLOCK_SPEED = 1
UPDATE_THRESHOLD = 60
TIMEOUT_THRESHOLD = 10
TIMEOUT_DELAY = 1
WIFI_DELAY = 30
TEMP_OFFSET = -2
HUM_OFFSET = 8


# ------------------------- DEVICE INFO ------------------------- #

PICO_NAME = confsec.HOSTNAME
PICO_ROOM = "Unassigned"


# ------------------------- PIN CONFIG ------------------------- #

BME_SDA_PIN = 4
BME_SCL_PIN = 5
OLED_SDA_PIN = 6
OLED_SCL_PIN = 7


# ------------------------- NETWORK CONFIG ------------------------- #

WIFI_SSID = confsec.WSSID
WIFI_PASSWORD = confsec.WPASSWD
CSV_FILE = "PICO_DATA.csv"
SERVER_URL = confsec.API_QUERY
FORM_MAP = confsec.API_MAP

REPORTING_TIMES = [
    "08:00:00", # 8:00am
    "10:00:00", # 10:00am 
    "12:00:00", # 12:00pm
    "14:00:00", # 2:00pm
    "16:00:00"  # 4:00pm
]