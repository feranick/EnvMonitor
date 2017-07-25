#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170725f
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

PMtimewait = 5

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
    ''' Make JSON and push to MongoDB '''
    #************************************
    conn = GEmongoDB(sensData,mongoFile)
    print("\n JSON:\n",conn.makeJSON(),"\n")
    print(" Pushing to MongoDB:")
    conn.pushToMongoDB()

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
''' Class Database '''
#************************************
class GEmongoDB:
    def __init__(self, data, file):
        self.data = data
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

    def makeJSON(self):
        dataj = {
            'lab' : self.data[0],
            'IP' : self.data[1],
            'date' : self.data[2],
            'time' : self.data[3],
            'temperature' : '{0:0.1f}'.format(self.data[4]),
            'pressure' : '{0:0.1f}'.format(self.data[5]),
            'humidity' : '{0:0.1f}'.format(self.data[6]),
            }
        return json.dumps(dataj)
    
    def pushToMongoDB(self):
        jsonData = self.makeJSON()
        client = self.connectDB()
        db = client.Tata
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(jsonData))
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
