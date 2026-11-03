"""
Author: dev.slife
Contributors: Chris Hawley
Date Created: 2/19/26
Date Updated: 11/3/26
Description: Connects to the network and manages HTTP requests using REST.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import gc
import ubinascii
import urequests
import network
import time
from .errlog import log_error
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
# A POST takes about 1s. With a 1s timeout, timed out attempts leaked memory until the next
# reset, so every later POST failed with ENOMEM; timeouts at 10s haven't shown that.
HTTP_TIMEOUT = 10
HTTP_ATTEMPTS = 3
# umd-iot drops POSTs of some exact sizes (no reply, every time). Each retry adds a header
# of a different length (ignored by the form) so a dropped size isn't repeated.
RETRY_PADDING = (0, 5, 13)
# seconds to wait between failed POST attempts
RETRY_DELAY = 5
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
        log_error(f"WARNING: Connection timed out, unable to connect to {WIFI_SSID}. Please make sure you have the correct SSID and password set.  WLAN Status: {WLAN.status()}")
    

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


def send_payload(payload: dict, headers={}, low_load=False, include_time=False):
    """
    Sends a given payload by breaking it down into smaller chunks to prevent timeout errors.
    The room is never sent; the form's script fills it in from the configuration sheet.
    
    Args:
        payload (dict) - the data to send
        headers (dict) - the HTTP POST headers
        include_time (bool) - send when the reading was taken, for queued readings sent late.
            Otherwise the form uses the time it received the reading.
    """
    chunksToLoad = [
        ["Unique ID", "Hour Recorded", "Minute Recorded", "Time Recorded"],
        ["Unique ID", "Year Recorded", "Month Recorded", "Day Recorded", "Date Recorded"],
        ["Unique ID", "Raw Temperature", "Temperature"],
        ["Unique ID", "Raw Humidity", "Humidity"]
    ] if (not low_load) else [
        ["Unique ID", "Raw Temperature", "Raw Humidity"] + ([
            "Year Recorded", "Month Recorded", "Day Recorded", "Hour Recorded", "Minute Recorded"
        ] if (include_time) else [])
    ]
    payloadChunks = []
    for chunk in chunksToLoad:
        payloadChunks.append([FORM_MAP[key] for key in chunk])
    for chunk in payloadChunks:
        subload = {key: payload[key] for key in chunk if key in payload}
        response = urequests.post(SERVER_URL, data=url_encode(subload), headers=headers, timeout=HTTP_TIMEOUT)
        response.close()


def http_send(payload: dict, include_time=False, max_attempts=HTTP_ATTEMPTS):
    """
    Sends an HTTP POST request to the Raspberry Pi Pico Data Collector form.
    
    Args:
        payload (dict) - the data to send
        include_time (bool) - send when the reading was taken (see send_payload)
        max_attempts (int) - the amount of attempts it uses to POST
    """
    if (has_wifi()):
        err_reasons = set()
        for i in range(max_attempts):
            if (i > 0):
                time.sleep(RETRY_DELAY)
            # free the previous attempt's buffers before opening a new connection
            gc.collect()
            try:
                headers = {
                    "Host": "docs.google.com",
                    "User-Agent":  "RaspberryPi"+PICO_NAME,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                padding = RETRY_PADDING[i % len(RETRY_PADDING)]
                if (padding):
                    headers["X-Pad"] = "x" * padding
                send_payload(payload, headers=headers, low_load=True, include_time=include_time)
                print("Payload successfully POST.")
                return True
            except Exception as e:
                err_reasons.add(f"{type(e).__name__}: {e}")
        log_error(f"Failed to POST after {max_attempts} attempts, Given Errors: [{", ".join(err_reasons)}]")
    return False