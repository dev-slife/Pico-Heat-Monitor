"""
Author: dev.slife
Date Created: 2/19/26
Date Updated: 4/1/26
Description: Connects to the network and manages HTTP requests using REST.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import ubinascii
import urequests
import network
import time
from .config import \
    WIFI_SSID, \
    WIFI_PASSWORD, \
    SERVER_URL, \
    PICO_NAME, \
    TIMEOUT_THRESHOLD, \
    TIMEOUT_DELAY


# ------------------------ CONSTANTS ------------------------ #

TIME_SERVER = "https://timeapi.io/api/v1/time/current/zone?timezone=America%2FNew_York"
WLAN = network.WLAN(network.STA_IF)
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
        print(f"WARNING: Connection timed out, unable to connect to {WIFI_SSID}. Please make sure you have the correct SSID and password set.")
    

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


def http_send(payload: dict, max_attempts=5):
    """
    Sends an HTTP POST request to the Raspberry Pi Pico Data Collector form.
    
    Args:
        payload (dict) - the data to send
        max_attempts (int) - the amount of attempts it uses to POST
    """
    if (has_wifi()):
        for i in range(max_attempts):
            try:
                headers = {
                    "Host": "docs.google.com",
                    "User-Agent":  "RaspberryPi"+PICO_NAME,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                response = urequests.post(SERVER_URL, data=url_encode(payload), headers=headers, timeout=5)
                print(f"HTTP Status: {response.status_code}")
                response.close()
                return True
            except Exception as e:
                print(f"[{i}] A(n) {type(e).__name__} occurred: {e}")
        print("Failed to POST.")
    return False


def http_request(max_attempts=5):
    """
    Sends an HTTP GET request to timeapi.io for grabbing timezone data.
    
    Args:
        max_attempts (int) - the amount of attempts it uses to GET
    """
    if (has_wifi()):
        for i in range(max_attempts):
            try:
                response = urequests.get(TIME_SERVER, timeout=5)
                print(f"HTTP Status: {response.status_code}")
                return response.json()
            except Exception as e:
                print(f"[{i}] A(n) {type(e).__name__} occurred: {e}")
        print("Failed to GET.")
    return False