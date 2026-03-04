"""
Author: dev.slife
Date Created: 2/19/26
Date Updated: 3/4/26
Description: Holds configuration values for Pico Heat Monitor.
"""

# ------------------------- SPEED CONFIG ------------------------- #

CLOCK_SPEED = 1
UPDATE_THRESHOLD = 60


# ------------------------- DEVICE INFO ------------------------- #

PICO_NAME = "Pico<#1>"
PICO_ROOM = "Room<#1>"


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