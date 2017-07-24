# EnvMonitor
Record Enviromental Parameters

Track relative humidity (RH), Temperature (T) and pressure (P) continuously with timestamp 
and location in several relevant location and submit to DB independently of experiment. 
Connection between exp. and environmental tracking data is done through the database with no 
user intervention (as long as the user lists the right time/date/location). Parameters to 
track RH/T.

Requirements
============
- Raspberry Pi
- Adafruit BME280
- Shinyei PPD42NS particulate sensor (under development)
  - data sheet: http://www.mouser.com/ds/2/744/Seeed_101020012-838657.pdf

Installation
============
	sudo apt-get update
	sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
    mkdir ~/software
    cd ~/software
	git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
	cd Adafruit_Python_GPIO
	sudo python3 setup.py install
    cd ..
	git clone https://github.com/adafruit/Adafruit_Python_BME280.git
    cd Adafruit_Python_BME280
    sudo python3 setup.py install

	
Usage:
======
 	python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongodb-auth-file>
    
The software will be automated through a script (EnvMonitor_launcher.sh). Since the RPi is 
connected online via WiFi-DHCP, the IP may change. Through this script, the IP is collected
on boot and saved on a dedicated server. This is achieved by adding the following to /etc/rc.local:

su pi -c 'home/pi/EnvMonitor/EnvMonitor_launcher.sh'

The same script will eventually run the software itself
at periodic intervals. 
    

