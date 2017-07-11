#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170711a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, time, json
#from Adafruit_BME280 import *

global MongoDBhost

def main():
    if len(sys.argv)<2:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor_class.py <lab-identifier>\n')
        return
    
    lab = sys.argv[1]
    MongoDBhost = 'localhost:27017'
    sensor1 = Sensor(lab)
    sensor1.readSensors()
    sensor1.printUI()
    
    print(sensor1.makeJSON())
    
    #sensors1.pushToMongoDB()

#************************************
''' Class Sensor '''
#************************************
class Sensor:
    def __init__(self, lab):
        self.lab = lab
        self.date = time.strftime("%Y%m%d")
        self.time = time.strftime("%H:%M:%S")
        self.sensData = []

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
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.3f} deg C".format(self.sensData[0]))
        print(" Pressure = {0:0.2f} hPa".format(self.sensData[1]))
        print(" Humidity = {0:0.2f} %".format(self.sensData[2]),"\n")


    #************************************
    ''' Make JSON '''
    #************************************
    def makeJSON(self):
        data = {
            'lab' : self.lab,
            'date' : self.date,
            'time' : self.time,
            'temperature' : self.sensData[0],
            'pressure' : self.sensData[1],
            'humidity' : self.sensData[2]
        }
        return json.dumps(data)
        
    #****************************************
    ''' Push to Mongo  - non functional '''
    #****************************************
    def pushToMongoDB(self):
        from pymongo import MongoClient
        client = MongoClient(MongoDBhost)
        db = client.Tata
        db.EnvTrack.insert_one(makeJSON(self))

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
