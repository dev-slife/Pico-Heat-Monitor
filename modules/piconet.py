"""
Author: dev.slife
Date Created: 2/19/26
Date Updated: 5/14/26
Description: Connects to the network and manages HTTP requests using REST.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import ubinascii
import urequests
import network
import time
from .config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    FORM_MAP,
    SERVER_URL,
    PICO_NAME,
    TIMEOUT_THRESHOLD,
    TIMEOUT_DELAY
)


# ------------------------ CONSTANTS ------------------------ #

TIME_SERVER = "https://timeapi.io/api/v1/time/current/zone?timezone=America%2FNew_York"
WLAN = network.WLAN(network.WLAN.IF_STA)
WLAN.active(True)


# ----------------------- NETWORK FUNCTIONS ----------------------- #

def has_wifi():
    """
    Checks to see if the Pico is connected to WiFi.
    
    Returns:
        True if there is a wifi connection and False otherwise.
    """
    return WLAN.isconnected()


def disconnect_wifi():
    """Disconnects the Pico from the network."""
    WLAN.disconnect()
    print(f"Disconnected from {WIFI_SSID}")


def connect_wifi():
    """Connects the Pico to the network."""
    count = 0
    print(f"Mac Address is {grab_MAC()}")

    if not has_wifi():
        print(f"Attempting to connect to {WIFI_SSID}...")
        WLAN.connect(WIFI_SSID, WIFI_PASSWORD)

        while not has_wifi() and count < TIMEOUT_THRESHOLD:
            time.sleep(TIMEOUT_DELAY)
            count += 1
    
    if (has_wifi()):    
        print("Network config:", WLAN.ifconfig())
    else:
        disconnect_wifi()
        print(f"WARNING: Connection timed out, unable to connect to {WIFI_SSID}. Please make sure you have the correct SSID and password set.  WLAN Status:{WLAN.status}")
    

def grab_MAC():
    """
    Grabs the MAC address of the Raspberry Pi Pico.
    
    Returns:
        A string representing the MAC address of the Pico.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return ubinascii.hexlify(wlan.config('mac'),':').decode()



# ----------------------- HTTP FUNCTIONS ----------------------- #

def url_encode(data: dict):
    """
    Encodes a given dictionary into a url format.
    
    Args:
        data (dict) - the data given
    """
    parts = []
    for key, value in data.items():
        parts.append(f"{key}={str(value).replace(" ", "+")}")
    return "&".join(parts)


def send_payload(payload: dict, headers={}, low_load=False):
    """
    Sends a given payload by breaking it down into smaller chunks to prevent timeout errors.
    
    Args:
        payload (dict) - the data to send
        headers (dict) - the HTTP POST headers
    """
    chunksToLoad = [
        ["Unique ID", "Assigned Room", "Hour Recorded", "Minute Recorded", "Time Recorded"],
        ["Unique ID", "Year Recorded", "Month Recorded", "Day Recorded", "Date Recorded"],
        ["Unique ID", "Raw Temperature", "Temperature"],
        ["Unique ID", "Raw Humidity", "Humidity"]
    ] if (not low_load) else [
        ["Unique ID", "Assigned Room", "Raw Temperature", "Raw Humidity"]
    ]
    payloadChunks = []
    for chunk in chunksToLoad:
        payloadChunks.append([FORM_MAP[key] for key in chunk])
    for chunk in payloadChunks:
        subload = {key: payload[key] for key in chunk if key in payload}
        response = urequests.post(SERVER_URL, data=url_encode(subload), headers=headers, timeout=TIMEOUT_DELAY)
        response.close()


def http_send(payload: dict, max_attempts=TIMEOUT_THRESHOLD):
    """
    Sends an HTTP POST request to the Raspberry Pi Pico Data Collector form.
    
    Args:
        payload (dict) - the data to send
        max_attempts (int) - the amount of attempts it uses to POST
    """
    if (has_wifi()):
        for i in range(max_attempts):
            err_reasons = set()
            try:
                headers = {
                    "Host": "docs.google.com",
                    "User-Agent":  "RaspberryPi"+PICO_NAME,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                send_payload(payload, headers=headers, low_load=True)
                print("Payload successfully POST.")
                return True
            except Exception as e:
                err_reasons.add(f"{type(e).__name__}: {e}")
        print(f"Failed to POST, Given Errors: [{", ".join(err_reasons)}]")
    return False