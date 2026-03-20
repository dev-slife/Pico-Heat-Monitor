"""
Author: dev.slife
Date Created: 2/18/26
Date Updated: 3/20/26
Description: Handles local time and date information.
"""


# ---------------------- IMPORT MODULES ---------------------- #

from .piconet import connect_wifi
import ntptime
import time


# ------------------------ CONSTANTS ------------------------ #

# Month mapping
MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

# Connect to WiFi
WLAN = connect_wifi()



# ----------------------- GRAB LOCAL TIME ----------------------- #

def getLocalTime():
    """Grabs the local time."""
    try:
        ntptime.settime()
    except OSError as e:
        print(f"An {type(e).__name__} occurred: {e}")
            
    return time.localtime()



# ----------------------- GRAB LOCAL TIME ----------------------- #

def local_inc_time(curTime: str, incType: str, amount: int=1):
    """
    Locally increments the time, so network communication isn't needed.
    
    Args:
        curTime (str) - The given current time
        incType (str) - The type to increment:
            - 'h' for hour
            - 'm' for minute
            - 's' for second
        amount (int) - The amount to increment by
        
    Returns:
        The new incremented time
    """
    if (incType in ['h', 'm', 's']):
        h, m, s, = map(int, curTime.split(":"))
        
        # increment
        s = s+amount if incType == 's' else s
        m = m+amount if incType == 'm' else m
        h = h+amount if incType == 'h' else h
        
        # update values to be in proper format
        while (s >= 60 or m >= 60 or h >= 24):
            if (s >= 60):
                m = m+1
                s = s-60
            if (m >= 60):
                h = h+1
                m = m-60
            if (h >= 24):
                h = 0
                m = 0
                s = 0
        
        # return values
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        print("WARNING: could not increment given time; invalid incType given.")



# ----------------------- FORMATTING ----------------------- #

def format_MonthDDYr(m: int, d: int, y: int) -> str:
    """
    Formats a date in Month DD Yr
    
    Args:
        m (int) - the given month number
        d (int) - the given day
        y (int) - the given year
        
    Returns:
        The date in the Month DD Yr format
    """
    return f"{MONTHS[m - 1]} {d:02d} {y}"


def format_MMDDYY(date=None, m=None, d=None, y=None):
    """
    Formats a date in MM/DD/YY.
    
    Args:
        m (str) - the given month name
        d (int) - the given day
        y (int) - the given year
        
    Returns:
        The date in the MM/DD/YY format
    """
    if (date and isinstance(date, str)): m, d, y = date.split(" ")
    if (m and d and y):
        return f"{MONTHS.index(m)}/{int(d):02d}/{str(y)[2:]}"
    else:
        print("WARNING: Date could not be properly formatted.")
    


# ----------------------- CONVERSIONS ----------------------- #

def get_date() -> str:
    """
    Grabs the date from the given local time.
        
    Returns:
        A string representing the date.
    """
    localTime = getLocalTime()
    return format_MonthDDYr(localTime[1], localTime[2], localTime[0])
 

def get_time() -> str:
    """
    Grabs the time from the current local time.
        
    Returns:
        A string representing the time.
    """
    def format(unit: int) -> str:
        """
        Fixes the format for the given time unit.
        
        Args:
            unit (int) - the unit to format
        
        Returns:
            A string with the correct time format.
        """
        return str(unit) if unit >= 10 else f"0{unit}"
    
    # Hours, Minutes, Seconds
    # subtract 5 from hours to convert from UTC to EST
    localTime = getLocalTime()
    return f"{format(localTime[3] - 5)}:{format(localTime[4])}:{format(localTime[5])}"