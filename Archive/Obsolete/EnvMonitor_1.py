#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170724a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, time, json, os.path
from Adafruit_BME280 import *

global MongoDBhost

def main():
    if len(sys.argv)<3 or os.path.isfile(sys.argv[2]) == False:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongoFile>\n')
        return
    
    mongoFile = sys.argv[2]

    lab = sys.argv[1]
    sensor1 = Sensor(lab)
    sensor1.readSensors()
    sensor1.printUI()
        
    print(" JSON:\n",sensor1.makeJSON(),"\n")
    
    print(" Pushing to MongoDB:")
    sensor1.pushToMongoDB(mongoFile)

#************************************
''' Class Sensor '''
#************************************
class Sensor:
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
