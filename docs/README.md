# Pico Heat Monitor
A Micropython program coded for the Raspberry Pi Pico 2W which tracks temperature and humidity levels.


## Installing Pico Heat Monitor

### Fetching The Drivers
1. Go to the official [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) and follow the instructions to download the firmware for your specific Pico device.
2. Download the BME280 + ssd1306 OLED Drivers from (will be documented soon...)

### Setting Up Pico For VSCode
Skip this step if you have a different IDE you would prefer to use.
1. Install the official Raspberry Pi Pico extension
[Screenshot of Raspberry Pi Pico extension](../docs/images/Pico%20Extension.png)
2. Select the Raspberry Pi icon now on the left sidebar of VSCode or click the sidebar menu and press the button named, "Raspberry Pi Pico Project" to create a new project
[Screenshot for making a new Pico project](../docs/images/Pico%20Project.png)
3. Wire your jumper cables to the appropriate pins
    - Power (Red recommended) -> 3v3 pin
    - Ground (Black recommended) -> Any GND pin
    - BME280 SDA -> GP4
    - BME280 SCL -> GP5
    - OLED SDA -> GP6
    - OLED SCL -> GP7
4. Plug in the Pico to an available USB port on your computer
5. Ensure that your IDE recognizes your Pico and your pins are wired correctly
[Screenshot showing the IDE recognizes the Pico](../docs/images/Pico%20Connected.png)
6. You should see a button called, "Toggle Mpy FS" at the bottom of VSCode. Click that to open up your Pico's workspace
[Screenshot of Toggle Mpy FS button](../docs/images/Pico%20Toggle.png)
[Screenshot of Pico Workspace](../docs/images/Pico%20Workspace.png)
7. Copy all files from this repo and move it into the Pico's workspace
#### Extra Notes 
- You can change the BME280 and OLED pins to your preference, just remember to also change them in [config.py](../modules/config.py)
- For more information on Raspberry Pi Pico & VSCode see: *[Get started with Raspberry Pi Pico-series and VS Code](https://www.raspberrypi.com/news/get-started-with-raspberry-pi-pico-series-and-vs-code/)*

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
Find a power adapter to plug in your Pico 2W to a wall outlet. It is not recommended to plug the cable straight into a USB port that gives power, unless it is through a trusted device.

### Using An IDE
Plug in your Pico 2W to a USB port on your computer. Open up your preferred IDE and make sure that it recognizes your Pico. Run the [main.py](../main.py) file to run the whole program.


## Configuration Values
There are multiple different values which can be changed to your preference when using Pico Heat Monitor (found in: [config.py](../modules/config.py)).
- `CLOCK_SPEED`: The rate at which [main.py](../main.py) executes the `main()` function. Only impacts how the local time increments and is shown on the OLED screen
- `UPDATE_THRESHOLD`: How often the Pico sends an HTTP request to the Google form and adds data to its local CSV file
- `PICO_NAME`: The name of the Pico (used for building data)
- `PICO_ROOM`: The room your Pico is in (used for building data)
- `WIFI_SSD`: Your network SSID (WiFi name)
- `WIFI_PASSWORD`: Your network password
- `SERVER_URL`: The url for your google form (should end in /formResponse)
- `FORM_MAP`: A dictionary mapping the entry ids for each prompt (entry.xxxxx)


## Notable Functions
Will be documented soon...