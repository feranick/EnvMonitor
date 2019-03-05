#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking
* version: 20190304b
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

#***************************************************
''' This is needed for installation through pip '''
#***************************************************
def EnvMonitor():
    main()
#***************************************************

import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
import numpy as np
from libEnvMonitor import *
from Adafruit_BME280 import *
import RPi.GPIO as GPIO

#************************************
''' Main - Scheduler '''
#************************************
def main():
    s = sched.scheduler(time.time, time.sleep)
    conf = Configuration()
    if os.path.isfile(conf.configFile) is False:
        print("Configuration file does not exist: Creating one.")
        conf.createConfig()
    conf.readConfig(conf.configFile)
    while True:
        s.enter(conf.runSeconds, conf.sleepSeconds, runAcq)
        s.run()

#************************************
''' Run Acquistion '''
#************************************
def runAcq():
    conf = Configuration()
    conf.readConfig(conf.configFile)
    
    #************************************
    ''' NEW: Read from T/RH sensor '''
    #************************************
    trhSensor = TRHSensor(conf)
    sensData = trhSensor.readSensors()
    trhSensor.printUI()
    try:
        conn = SubMongoDB(json.dumps(sensData),conf)
        #conn.checkCreateLotDM(sub)
        conn.pushToMongoDB()
    except:
        print("\n Submission to database failed!\n")

#************************************
''' Class T/RH Sensor '''
#************************************
class TRHSensor:
    def __init__(self, config):
        #config = Configuration()
        #config.readConfig(config.configFile)
        self.date = time.strftime("%Y%m%d")
        self.time = time.strftime("%H:%M:%S")
        self.sensData = []
        self.ip = getIP()
        self.lab = config.lab
        self.measType = config.measType
    
    #************************************
    ''' Read Sensors '''
    #************************************
    def readSensors(self):
        self.sensData.extend([self.lab, self.measType, self.ip, self.date, self.time])
        try:
            sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
            self.sensData.extend([sensor.read_temperature(),
                                  sensor.read_pressure() / 100,
                                  sensor.read_humidity()])
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.sensData.extend([0,0,0])
    
        dataj = {
            'lab' : self.sensData[0],
            'measType' : self.sensData[1],
            'IP' : self.sensData[2],
            'date' : self.sensData[3],
            'time' : self.sensData[4],
            'temperature' : '{0:0.1f}'.format(self.sensData[5]),
            'pressure' : '{0:0.1f}'.format(self.sensData[6]),
            'humidity' : '{0:0.1f}'.format(self.sensData[7]),
            }
        #return json.dumps(dataj)
        return dataj
        
    #************************************
    ''' Print Values on screen '''
    #************************************
    def printUI(self):
        print("\n Lab: ", self.lab)
        print(" Measurement type: ", self.measType)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.1f} deg C".format(self.sensData[5]))
        print(" Pressure = {0:0.1f} hPa".format(self.sensData[6]))
        print(" Humidity = {0:0.1f} %".format(self.sensData[7]),"\n")

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
