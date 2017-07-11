#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking
* version: 20170711a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, time, json
global MongoDBhost

global MongoDBhost

def main():
    if len(sys.argv)<2:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor.py <lab-identifier>\n')
        return

    import time
    lab = sys.argv[1]
    MongoDBhost = 'localhost:27017'
    date = time.strftime("%Y%m%d")
    time = time.strftime("%H:%M:%S")

    sensData = readSensors()
    printUI(lab, date, time, sensData)
    json = makeJSON(lab, date, time, sensData)
    print(json)
    #pushToMongoDB(json)

#************************************
''' Read Sensors '''
#************************************
def readSensors():
    #from Adafruit_BME280 import *
    sensData = []
    try:
        sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
        sensData.append(sensor.read_temperature())
        sensData.append(sensor.read_pressure() / 100)
        sensData.append(sensor.read_humidity())
    except:
        print("\n SENSOR NOT CONNECTED ")
        sensData.append(0.0)
        sensData.append(0.0/100)
        sensData.append(0.0)
        return sensData

#************************************
''' Print Values on screen '''
#************************************
def printUI(lab, date, time, sensData):
    print("\n Lab: ", lab)
    print(" Date: ", date)
    print(" Time: ", time)
    print(" Temperature = {0:0.3f} deg C".format(sensData[0]))
    print(" Pressure = {0:0.2f} hPa".format(sensData[1]))
    print(" Humidity = {0:0.2f} %".format(sensData[2]),"\n")

#************************************
''' Make JSON '''
#************************************
def makeJSON(lab, date, time, sensData):
    data = {
        'lab' : lab,
            'date' : date,
            'time' : time,
            'temperature' : sensData[0],
            'pressure' : sensData[1],
            'humidity' : sensData[2]
        }
    return json.dumps(data)

#****************************************
''' Push to Mongo  - non functional '''
#****************************************
def pushToMongoDB(json):
    from pymongo import MongoClient
    client = MongoClient(MongoDBhost)
    db = client.Tata
    db.EnvTrack.insert_one(json)

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
