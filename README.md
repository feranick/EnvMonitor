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

Installation
============
	sudo apt-get update
	sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
	git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
	cd Adafruit_Python_GPIO
	sudo python setup.py install
	git clone https://github.com/adafruit/Adafruit_Python_BME280.git
	
Usage:
======
 	python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongodb-auth-file>

