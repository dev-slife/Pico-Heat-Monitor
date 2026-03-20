"""
Author: dev.slife
Date Created: 2/18/26
Date Updated: 3/20/26
Description: Builds and manages a csv file.
"""


# ---------------------- IMPORT MODULES ---------------------- #

import os
from collections import OrderedDict
from modules.config import FORM_MAP


# ------------------------ CONSTANTS ------------------------ #

# CSV file name
CSV_FILE = "PICO_DATA.csv"



# ---------------------- OS HANDLING ---------------------- #

def file_exists(filename: str) -> bool:
    """
    Checks to see if a file exists.
    
    Args:
        filename (str) - the name of the file
    
    Returns:
        True if it does, False if not.
    """
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
    

def pico_storage():
    """
    Grabs all storage data for the Raspberry Pi Pico 2W.
    
    Returns:
        An OrderedDict of all storage statistics 
    """
    # Get file system statistics
    try:
        stat = os.statvfs('/')
        size_bytes = stat[1] * stat[2]
        free_bytes = stat[0] * stat[3]
        used_bytes = size_bytes - free_bytes
        return OrderedDict([
            ("Bytes", OrderedDict([
                ("Size", size_bytes),
                ("Free", free_bytes),
                ("Used", used_bytes)
            ])),
            ("KB", OrderedDict([
                ("Size", size_bytes / 1024),
                ("Free", free_bytes / 1024),
                ("Used", used_bytes / 1024)
            ])),
            ("MB", OrderedDict([
                ("Size", size_bytes / (1024**2)),
                ("Free", free_bytes / (1024**2)),
                ("Used", used_bytes / (1024**2))
            ]))
        ])
    except Exception as e:
        print(f"A(n) {type(e).__name__} occurred: {e}")
    

def pico_available():
    """Grabs the available space (in MB) that the Pico has."""
    data = pico_storage()
    if data: return data["MB"]["Free"]



# ---------------------- DATA MANAGING ---------------------- #

def csv_append(data: dict):
    """
    Appends data to the local csv file.
    
    Args:
        data (dict) - the given data
    
    Side effects:
        Writes or appends data to the local csv file.
    """
    if (file_exists(CSV_FILE)):
        with open(CSV_FILE, mode='a') as file:
            line = ""
            values = list(data.values())
            for i in range(len(values)):
                line += str(values[i]) + "," if (i != len(values) - 1) else str(values[i])
            line += "\n"
            file.write(line)
    else:
        new_data = [list(data.keys()), list(data.values())]
        with open(CSV_FILE, mode='w') as file:
            index = 0
            while (index < 2):
                line = ""
                values = new_data[index]
                for i in range(len(values)):
                    line += str(values[i]) + "," if (i != len(values) - 1) else str(values[i])
                line += "\n"
                index += 1
                file.write(line)

                   
def csv_overwrite(lines: list):
    """
    Overwrites data in the local csv file.
    
    Args:
        lines (list) - the lines to write to the file
        
    Side effects:
        Writes or appends data to the local csv file.
    """
    with open(CSV_FILE, mode='w') as file:
        file.write("".join(lines))


def csv_remove(rows: tuple):
    """
    Removes data from the local csv file.
    
    Args:
        rows (tuple) - the row indices to remove
        
    Side effects:
        Writes or appends data to the local csv file.
    """
    if (file_exists(CSV_FILE)):
        with open(CSV_FILE, mode='r') as file:
            lines = file.readlines()
        if (lines):
            data = [lines[i] for i in range(len(lines)) if ((i not in rows) or (i == 0))]
            csv_overwrite(data)
            print(f"Removed lines {rows} from {CSV_FILE}")
     
       
def csv_count_rows() -> int:
    """
    Counts the amount of rows in the local csv file.
    """
    rows = 0
    with open(CSV_FILE, mode='r') as file:
        data = file.read()
        for char in data:
            if (char == "\n"): rows += 1
    return rows    
  
     
def csv_clear():
    """
    Clears all data in the local csv file.
    
    Side effects:
        Writes or appends data to the local csv file.
    """
    if (file_exists(CSV_FILE)):
        csv_remove((1, csv_count_rows() - 1))
    


# ---------------------- DATA CONVERSION ---------------------- #

def serializeCSV():
    """
    Converts {CSV_FILE} into a Python dictionary format.
        
    Return:
        A list of dictionaries representing {CSV_FILE}
    """
    if (file_exists(CSV_FILE)):
        payloads = []
        data = OrderedDict()
        parse = ""
        keys = True
        i = 0
        line = 0
        with open(CSV_FILE, mode='r') as file:
            for char in file.read():
                if (char == "," or char == "\n"):
                    if (keys):
                        if (char == "\n"): keys = False
                        data[FORM_MAP[parse]] = ""
                    else:
                        data[list(data.keys())[i]] = parse
                        if (char == "\n"):
                            payloads.append((data.copy(), line))
                    if (char == "\n"):
                        i = 0
                        line += 1
                    else:
                        i += 1
                    parse = ""
                else:
                    parse += char
        return payloads
    else:
        print(f"WARNING: Unable to locate {CSV_FILE}; does not exist")
        
        

# Just To Check Space Manually
if __name__ == "__main__":
    print(f"Pico space: {pico_storage()}")
    print(f"Free space: {pico_available():.2f} MB")