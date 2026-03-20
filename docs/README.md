# Pico Heat Monitor
A Micropython program coded for the Raspberry Pi Pico 2W which tracks temperature and humidity levels.


## Installing Pico Heat Monitor

### Fetching The Drivers
Go to the official [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) and follow the instructions to download the firmware for your specific Pico device.

### Setting Up Pico For VSCode
Skip this step if you have a different IDE you would prefer to use.
1. Install the official Raspberry Pi Pico extension
![Screenshot of Raspberry Pi Pico extension](../docs/images/Pico%20Extension.png)
2. Select the Raspberry Pi icon now on the left sidebar of VSCode or click the sidebar menu and press the button named, "Raspberry Pi Pico Project" to create a new project
![Screenshot for making a new Pico project](../docs/images/Pico%20Project.png)
3. Wire your jumper cables to the appropriate pins
    - Power (Red recommended) -> 3v3 pin
    - Ground (Black recommended) -> Any GND pin
    - BME280 SDA -> GP4
    - BME280 SCL -> GP5
    - OLED SDA -> GP6
    - OLED SCL -> GP7
4. Plug in the Pico to an available USB port on your computer
5. Ensure that your IDE recognizes your Pico and your pins are wired correctly
![Screenshot showing the IDE recognizes the Pico](../docs/images/Pico%20Connected.png)
6. You should see a button called, "Toggle Mpy FS" at the bottom of VSCode. Click that to open up your Pico's workspace
![Screenshot of Toggle Mpy FS button](../docs/images/Pico%20Toggle.png)
![Screenshot of Pico Workspace](../docs/images/Pico%20Workspace.png)
7. Copy all files from this repo and move it into the Pico's workspace
> [!NOTE]
> You can change the BME280 and OLED pins to your preference, just remember to also change them in [config.py](../modules/config.py) (see [configuration values](#configuration-values))

> [!TIP]
> For more information on Raspberry Pi Pico & VSCode see: *[Get started with Raspberry Pi Pico-series and VS Code](https://www.raspberrypi.com/news/get-started-with-raspberry-pi-pico-series-and-vs-code/)*

### Configuring Your Heat Monitor
1. Open the [config.py](../modules/config.py) file and assign values to the following variables:
    - `WIFI_SSD`
    - `WIFI_PASSWORD`
    - `SERVER_URL`
    - `FORM_MAP`
2. Move all files to your Raspberry Pi Pico


## Running Pico Heat Monitor
You can run the Heat Monitor for your Raspberry Pi Pico 2W by either sending power straight to the Pico or by running the script through an IDE on your computer.

### Direct Power
Find a power adapter to plug in your Pico 2W to a wall outlet.
> [!CAUTION]
> It is not recommended to plug the cable straight into a USB port that gives power, unless it is through a trusted device.

### Using An IDE
Plug in your Pico 2W to a USB port on your computer. Open up your preferred IDE and make sure that it recognizes your Pico. Run the [main.py](../main.py) file to run the whole program.


## Configuration

### Notable Values
There are multiple different values which can be changed to your preference when using Pico Heat Monitor (found in: [config.py](../modules/config.py)).
- SPEED CONFIG
    - `CLOCK_SPEED`: The rate at which [main.py](../main.py) executes the `main()` function. Only impacts how the local time increments and is shown on the OLED screen
    - `UPDATE_THRESHOLD`: How often the Pico sends an HTTP request to the Google form and adds data to its local CSV file
- DEVICE INFO
    - `PICO_NAME`: The name of the Pico (used for building data)
    - `PICO_ROOM`: The room your Pico is in (used for building data)
- PIN CONFIG
    - `BME_SDA_PIN`: The GP number on the Raspberry Pi Pico for the BME280 SDA pin
    - `BME_SCL_PIN`: The GP number on the Raspberry Pi Pico for the BME280 SCL pin
    - `OLED_SDA_PIN`: The GP number on the Raspberry Pi Pico for the OLED SDA pin
    - `OLED_SCL_PIN`: The GP number on the Raspberry Pi Pico for the OLED SCL pin
- NETWORK CONFIG
    - `WIFI_SSD`: Your network SSID (WiFi name)
    - `WIFI_PASSWORD`: Your network password
    - `SERVER_URL`: The url for your google form (should end in /formResponse)
    - `FORM_MAP`: A dictionary mapping the entry ids for each prompt (entry.xxxxx)

### Connecting To WiFi
In order to have the Pico POST to a google form (or a preferred server), you need to be connected to the internet. Below are quick instructions to make sure your Raspberry Pi Pico can establish a connection.
1. Set up your WiFi or grab a trusted SSID.
2. Change `WIFI_SSID` to your WiFi SSID (name of the network)
3. Change `WIFI_PASSWORD` the password for your WiFi (leave blank if none)

### Connecting To A Google Form
The pico will attempt to send its data to a google form for every `UPDATE_THRESHOLD` that passes. If it fails to POST all data will be stored in, `PICO_DATA`, a local csv file. If you want to send data over to a google form, follow these steps:
1. Make sure you have your WiFi configured ([see Connecting To WiFi](#connecting-to-wifi))
2. Create a google form with the following entries (long answer text):
    - Unique ID
    - Assigned Room
    - Time Recorded
    - Date Recorded
    - Raw Temperature
    - Temperature
    - Raw Humidity
    - Humidity
3. Publish the form so that anyone with a link can respond
![Screenshot showing form options with anyone as a link being able to respond](./images/Pico%20Form.png)
4. Open the form as a responder
5. Press Ctrl+Shift+I or right-click and press "Inspect" to open inspect element
6. Go to the "Network" tab located at the top
7. Fill out the form with **different** values and submit it
8. Find your response on the left side panel and open the packet
9. On the right side panel click the "Headers" tab and copy the Request URL, this is the `SERVER_URL` (should end in /formResponse)
10. Click on the "Payload" tab and find your responses mapped with entry ids
![Screenshot showing payload tab with entries](./images/Pico%20Entries.png)
11. Assign each entry id to the proper key in the `FORM_MAP` configuration.

> [!WARNING]
> Make sure you have the correct entry id for each configuration value.

> [!IMPORTANT]
> Make sure you don't submit the form until after you have the "Network" tab open. You can delete the responses afterward.

> [!TIP]
> You can add or remove form entries if you decide to add or remove data you collect.


## Notable Functions
There are multiple key functions to keep in mind of which might help if you decide to make changes to the code.
### [picotime.py](../modules/picotime.py)
- `local_inc_time()`: locally increments the time to prevent unecessary network requests
    - `curTime` (str) - The current time
    - `incType` (str) - The type to increment
        - 'h' for hours
        - 'm' for minutes
        - 's' for seconds
    - `amount` (int) - The amount to increment by (default is 1)
- `get_time()`: grabs the local time
- `get_date()`: grabs the local date

### [picodata.py](../modules/picodata.py)
- `pico_storage()`: Grabs storage data for the Raspberry Pi Pico
    - This will return a dictionary of information
    - In bytes, KB, and MB
    - Shows storage size, free, and used space
    - use `pico_available()` for free space in MB
- `csv_append()`: Appends data to the local csv file stored on the Pico
    - `data` (dict) - the data to append
    - will write or change a csv file called `PICO_DATA`
    - Use `csv_overwrite()` to overwrite the CSV file
- `csv_remove()`: removes certain data from the local CSV file
    - `rows` (tuple) - the row indices to remove
    - use `csv_clear()` to clear all data from the local CSV file
- `serializeCSV()`: Converts the local CSV file data into payloads
    - Returns a list of payloads
    - each payload is a dictionary

### [piconet.py](../modules/piconet.py)
- `url_encode()`: Encodes a dictionary into url format
    - `data` (dict) - the given dictionary
    - used with `serializeCSV()`
- `http_send()`: Sends an HTTP POST request to `SERVER_URL`
    - `payload` (dict) - the payload to send
    - `max_attempts` (int) - the maximum amount of attempts before the POST fails