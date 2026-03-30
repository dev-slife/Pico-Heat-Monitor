"""
Author: dev.slife
Date Created: 2/19/26
Date Updated: 3/30/26
Description: Connects to the network and manages HTTP requests using REST.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import urequests
import network
import time
import ubinascii
from .config import WIFI_SSID, WIFI_PASSWORD, SERVER_URL, PICO_NAME


# ------------------------ CONSTANTS ------------------------ #

TIME_SERVER = "https://timeapi.io/api/v1/time/current/zone?timezone=America%2FNew_York"



# ----------------------- CONNECT TO WIFI ----------------------- #

def connect_wifi():
    """
    Connects the Pico 2W to the UMD IOT network.
    
    Returns:
        the wlan object.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        while not wlan.isconnected():
            time.sleep(1)
            
    print("Network config:", wlan.ifconfig())
    return wlan

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
    for i in range(max_attempts):
        try:
            response = urequests.get(TIME_SERVER, timeout=5)
            print(f"HTTP Status: {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"[{i}] A(n) {type(e).__name__} occurred: {e}")
    print("Failed to GET.")
    return False


# probably delete this later
if __name__ == "__main__":
    wlan = connect_wifi()
    wlan.active(True)
    print(ubinascii.hexlify(wlan.config('mac'),':').decode())