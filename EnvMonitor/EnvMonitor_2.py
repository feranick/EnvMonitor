#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170724c
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

def main():
    if len(sys.argv)<3 or os.path.isfile(sys.argv[2]) == False:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongoFile>\n')
        return
    
    mongoFile = sys.argv[2]

    lab = sys.argv[1]
    sensor1 = TRHSensor(lab)
    sensor1.readSensors()
    sensor1.printUI()
        
    print(" JSON:\n",sensor1.makeJSON(),"\n")

    pms = PMSensor(26)
    pms.read()


    #print(" Pushing to MongoDB:")
    #sensor1.pushToMongoDB(mongoFile)



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
        try:
            sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
            self.sensData.append(sensor.read_temperature())
            self.sensData.append(sensor.read_pressure() / 100)
            self.sensData.append(sensor.read_humidity())
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.sensData.append(0.0)
            self.sensData.append(0.0/100)
            self.sensData.append(0.0)
        return self.sensData

    #************************************
    ''' Print Values on screen '''
    #************************************
    def printUI(self):
        print("\n Lab: ", self.lab)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.1f} deg C".format(self.sensData[0]))
        print(" Pressure = {0:0.1f} hPa".format(self.sensData[1]))
        print(" Humidity = {0:0.1f} %".format(self.sensData[2]),"\n")

    #************************************
    ''' Make JSON '''
    #************************************
    def makeJSON(self):
        data = {
            'lab' : self.lab,
            'IP' : self.ip,
            'date' : self.date,
            'time' : self.time,
            'temperature' : '{0:0.1f}'.format(self.sensData[0]),
            'pressure' : '{0:0.1f}'.format(self.sensData[1]),
            'humidity' : '{0:0.1f}'.format(self.sensData[2])
        }
        return json.dumps(data)
        
    #****************************************
    ''' Push to Mongo '''
    #****************************************
    def pushToMongoDB(self, file):
        connDB1 = GEmongoDB(file)
        #connDB1.printAuthInfo()
        client = connDB1.connectDB()
        db = client.Tata
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(self.makeJSON()))
            print(" Data entry successful (id:",db_entry.inserted_id,")\n")
        except:
            print(" Data entry failed.\n")

#************************************
''' Class Particulate Sensor '''
#************************************
class PMSensor:
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
        self.gpio = gpio
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        
        self.duration = 0
        #self.starttime = time.time()
        self.sampletime_ms = 5 # 30s
        self.lowpulseoccupancy = 0
        self.rato = 0
        self.concentration = 0
        
        GPIO.setup(gpio,GPIO.OUT)

    def read(self):
        self.starttime = time.time()
        self.currenttime = 0
        while self.currenttime < self.sampletime_ms:
            self.currenttime = time.time()-self.starttime
            print('time:',str(self.currenttime))
            
            if GPIO.input(self.gpio) == 0:
                self.start = time.time()
            if GPIO.input(self.gpio) == 1:
                self.end = time.time()
                if self.end > self.end:
                    self.duration = self.end - self.start
                    self.lowpulseoccupancy = self.lowpulseoccupancy + self.duration
    
            #time.sleep (10)

        self.ratio = self.lowpulseoccupancy/(self.sampletime_ms*10.0);
        self.concentration = 1.1*pow(self.ratio,3)-3.8*pow(self.ratio,2)+520*self.ratio+0.62

        print(" Concentration:", self.concentration," pcs/0.01cf\n")
        self.lowpulseoccupancy = 0

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
