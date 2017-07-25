#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170725d
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, math, json, os.path, time
from Adafruit_BME280 import *
import RPi.GPIO as GPIO

global MongoDBhost

pms_gpio = 26

def main():
    if len(sys.argv)<3 or os.path.isfile(sys.argv[2]) == False:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongoFile>\n')
        return
    
    lab = sys.argv[1]
    mongoFile = sys.argv[2]
    
    #************************************
    ''' Read from T/RH sensor '''
    #************************************
    trhSensor = TRHSensor(lab)
    sensData = trhSensor.readSensors()
    trhSensor.printUI()
    
    #************************************
    ''' Read from PM sensor '''
    #************************************
    pms = PMSensor(pms_gpio)

    conc_imp, conc = pms.collect()
    print(" Particulate PM2.5: \n particles/m^3: {0:0.2f}".format(conc),
          "\n particles/cu-ft: {0:0.4f}".format(conc_imp))

    sensData.extend([conc])

    #************************************
    ''' Make JSON and push o '''
    #************************************
    print("\n JSON:\n",makeJSON(sensData),"\n")
    print(" Pushing to MongoDB:")
    #pushToMongoDB(sensData, mongoFile)


#************************************
''' Class T/RH Sensor '''
#************************************
class TRHSensor:
    def __init__(self, lab):
        self.lab = lab
        self.date = time.strftime("%Y%m%d")
        self.time = time.strftime("%H:%M:%S")
        self.sensData = []
        self.ip = getIP()

    #************************************
    ''' Read Sensors '''
    #************************************
    def readSensors(self):
        self.sensData.extend([self.lab, self.ip, self.date, self.time])
        try:
            sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
            self.sensData.extend([sensor.read_temperature(),
                                  sensor.read_pressure() / 100,
                                  sensor.read_humidity()])
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.sensData.extend([0.0,0.0,0.0])
        return self.sensData

    #************************************
    ''' Print Values on screen '''
    #************************************
    def printUI(self):
        print("\n Lab: ", self.lab)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.1f} deg C".format(self.sensData[4]))
        print(" Pressure = {0:0.1f} hPa".format(self.sensData[5]))
        print(" Humidity = {0:0.1f} %".format(self.sensData[6]),"\n")

#************************************
''' Class Particulate Sensor '''
#************************************
class PMSensor:
    
    import math, time
    import RPi.GPIO as GPIO

    """
    A class to read a Shinyei PPD42NS Dust Sensor, e.g. as used
    in the Grove dust sensor.

    This code calculates the percentage of low pulse time and
    calibrated concentration in particles per 1/100th of a cubic
    foot at user chosen intervals.

    You need to use a voltage divider to cut the sensor output
    voltage to a Pi safe 3.3V (alternatively use an in-line
    20k resistor to limit the current at your own risk).
    """

    def __init__(self, gpio):
        """
        Instantiate with the Pi and gpio to which the sensor
        is connected.
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(gpio,GPIO.IN)

        self.gpio = gpio
        self.collectionTime = 30

    def collect(self):
        runTime = time.time()
        lowpulseoccupancy = 0
        GPIO.remove_event_detect(self.gpio)
        GPIO.add_event_detect(self.gpio, GPIO.BOTH, bouncetime = 1)
        
        while time.time() - runTime < self.collectionTime:
            print(" Waiting",int(time.time() - runTime),
                  "/",int(self.collectionTime),"s for PM sensor...", end="\r")
            time.sleep(0.005)
            startTime = time.time()
            if GPIO.event_detected(self.gpio):
                GPIO.remove_event_detect(self.gpio)
                duration = time.time() - startTime
                lowpulseoccupancy = lowpulseoccupancy+duration
                GPIO.add_event_detect(self.gpio, GPIO.BOTH, bouncetime=1)
    
        ratio = lowpulseoccupancy*100/(self.collectionTime);
        conc_imp = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62
        conc = conc_imp*0.000238 # concentration in particles/L
        return (conc_imp, conc)

#************************************
''' Class Database '''
#************************************
class GEmongoDB:
    def __init__(self, file):
        with open(file, 'r') as f:
            f.readline()
            self.hostname = f.readline().rstrip('\n')
            f.readline()
            self.port_num = f.readline().rstrip('\n')
            f.readline()
            self.dbname = f.readline().rstrip('\n')
            f.readline()
            self.username = f.readline().rstrip('\n')
            f.readline()
            self.password = f.readline().rstrip('\n')

    def connectDB(self):
        from pymongo import MongoClient
        client = MongoClient(self.hostname, int(self.port_num))
        auth_status = client[self.dbname].authenticate(self.username, self.password, mechanism='SCRAM-SHA-1')
        print(' Authentication status = {0} \n'.format(auth_status))
        return client

    def printAuthInfo(self):
        print(self.hostname)
        print(self.port_num)
        print(self.dbname)
        print(self.username)
        print(self.password)

#************************************
''' Make JSON '''
#************************************
def makeJSON(data):
    data = {
        'lab' : data[0],
        'IP' : data[1],
        'date' : data[2],
        'time' : data[3],
        'temperature' : '{0:0.1f}'.format(data[4]),
        'pressure' : '{0:0.1f}'.format(data[5]),
        'humidity' : '{0:0.1f}'.format(data[6]),
        'PM2.5_particles_m3' : '{0:0.1f}'.format(data[7]),
    }
    return json.dumps(data)
    
#****************************************
''' Push to Mongo '''
#****************************************
def pushToMongoDB(json, file):
    connDB1 = GEmongoDB(file)
    #connDB1.printAuthInfo()
    client = connDB1.connectDB()
    db = client.Tata
    try:
        db_entry = db.EnvTrack.insert_one(json.loads(json))
        print(" Data entry successful (id:",db_entry.inserted_id,")\n")
    except:
        print(" Data entry failed.\n")

#************************************
''' Get system IP '''
#************************************
def getIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
