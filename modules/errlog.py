"""
Author: Chris Hawley
Date Created: 10/26/26
Date Updated: 11/3/26
Description: Keeps a persistent, size-capped error log on the Pico's flash.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import os
import time
from .picodata import file_exists


# ------------------------ CONSTANTS ------------------------ #

ERROR_LOG = "errors.log"
# when the log grows past this size it is moved to OLD_ERROR_LOG, keeping at most ~2x on flash
MAX_LOG_BYTES = 16 * 1024
OLD_ERROR_LOG = "errors.old.log"



# ---------------------- LOGGING ---------------------- #

def timestamp() -> str:
    """
    Builds a timestamp from the Pico's realtime clock.

    Returns:
        A string of the current date and time. Before the clock is synced
        this will be the RTC's default date (2021-01-01).
    """
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])


def log_error(message: str):
    """
    Prints a message and appends it to the error log with a timestamp.
    Never raises, so it is safe to call from inside an exception handler.

    Args:
        message (str) - the message to record

    Side effects:
        Appends to {ERROR_LOG}, rotating it to {OLD_ERROR_LOG} when it is too large.
    """
    print(message)
    try:
        if (file_exists(ERROR_LOG) and os.stat(ERROR_LOG)[6] >= MAX_LOG_BYTES):
            if (file_exists(OLD_ERROR_LOG)):
                os.remove(OLD_ERROR_LOG)
            os.rename(ERROR_LOG, OLD_ERROR_LOG)
        with open(ERROR_LOG, mode='a') as file:
            file.write(f"{timestamp()} {message}\n")
    except Exception as e:
        print(f"Unable to write to {ERROR_LOG}: {type(e).__name__}: {e}")
