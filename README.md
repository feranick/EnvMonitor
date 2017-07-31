# EnvMonitor
## Record Enviromental Parameters

Track temperature (T), pressure (P), relative humidity (RH), and particulate matter PM2.5 content
continuously with timestamp and location in several relevant locations and submit to DB independently of experiment. 
Connection between exp. and environmental tracking data is done through the database with no 
user intervention (as long as the user lists the right time/date/location).

## Requirements
- [Raspberry PI Zero W](https://www.raspberrypi.org/products/pi-zero-w/)
- [Adafruit BME280 T/P/RH sensor](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout)
- [Shinyei PPD42NS particle sensor](https://www.seeedstudio.com/Grove-Dust-Sensor-p-1050.html) ([data sheet](http://www.mouser.com/ds/2/744/Seeed_101020012-838657.pdf))
  
## Hardware Installation
### Adafruit BME280 T/P/RH sensor
    Vin -> pin4
    GND -> pin6
    SCK -> pin5
    SD1 -> pin3

### Shinyei PPD42NS particle sensor
This sensor requires a voltage divider to reduce the output voltage from 5V to 3.3V
    
    Red -> pin2
    Black -> pin9
    Yellow -> pin10    

This sensors require high frequency edge detection that is not supported by the rpi.gpio library. While that might change, in the meantime we rely on the [pigpio library](http://abyz.co.uk/rpi/pigpio/), a library for low level GPIO operations.  This is based on [this repo](https://github.com/andy-pi/weather-monitor)

## Software Installation
	sudo apt-get update
	sudo apt-get install build-essential python3-pip python3-dev python3-smbus git python3-rpi.gpio
    mkdir ~/software
    cd ~/software
	git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
	cd Adafruit_Python_GPIO
	sudo python3 setup.py install
    cd ..
	git clone https://github.com/adafruit/Adafruit_Python_BME280.git
    cd Adafruit_Python_BME280
    sudo python3 setup.py install
    wget abyz.co.uk/rpi/pigpio/pigpio.zip
    unzip pigpio.zip
    cd PIGPIO
    make
    sudo make install

## Usage
### T/P/RH sensor only:
    python3 EnvMonitor.py <lab-identifier> <mongodb-auth-file>
### T/P/RH and particle sensor
    sudo pigpiod
    python3 EnvMonitor_PM.py <lab-identifier> <mongodb-auth-file>
    
### Launcher    
The software will be automated through a script (EnvMonitor_launcher.sh). Since the RPi is 
connected online via WiFi-DHCP, the IP may change. Through this script, the IP is collected
on boot and saved on a dedicated server. This is achieved by adding the following to /etc/rc.local:

    su pi -c 'home/pi/EnvMonitor/EnvMonitor_launcher.sh'

The same script will eventually run the software itself at periodic intervals. 

## Contact
Nicola Ferralis <feranick@hotmail.com>
    

