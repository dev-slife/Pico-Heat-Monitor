"""
Author: dev.slife
Date Created: 2/19/26
Date Updated: 3/4/26
Description: Connects to the network and manages HTTP requests using REST.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import urequests
from ujson import dumps
import network
import time
import ubinascii
from .config import WIFI_SSID, WIFI_PASSWORD, SERVER_URL, PICO_NAME



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
    for _ in range(max_attempts):
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
            print(f"A(n) {type(e).__name__} occurred: {e}")
    print("Failed to POST.")
    return False


# probably delete this later
if __name__ == "__main__":
    wlan = connect_wifi()
    wlan.active(True)
    print(ubinascii.hexlify(wlan.config('mac'),':').decode())