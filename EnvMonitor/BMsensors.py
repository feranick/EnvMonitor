#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - BMsensors
* version: 20190305a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)
import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
import numpy as np
from libEnvMonitor import *
#from Adafruit_BME280 import *
#import Adafruit_BMP.BMP085 as BMP085
#import RPi.GPIO as GPIO

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
        self.BMsensor = config.BMsensor
    
    #************************************
    ''' Read Sensor BME280 '''
    #************************************
    def readSensors280(self):
        self.sensData.extend([self.lab, self.measType, self.BMsensor, self.ip, self.date, self.time])
        try:
             sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
             self.sensData.extend([sensor.read_temperature(),
                                  sensor.read_pressure() / 100])
             self.sensData.extend([sensor.read_humidity()])
             self.sensData.extend([sensor.read_dewpoint()])
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.sensData.extend([0,0,0,0])

        dataj = {
            'lab' : self.sensData[0],
            'measType' : self.sensData[1],
            'BMsensor' : self.sensData[2],
            'IP' : self.sensData[3],
            'date' : self.sensData[4],
            'time' : self.sensData[5],
            'temperature' : '{0:0.1f}'.format(self.sensData[6]),
            'pressure' : '{0:0.1f}'.format(self.sensData[7]),
            'humidity' : '{0:0.1f}'.format(self.sensData[8]),
            'dewpoint' : '{0:0.1f}'.format(self.sensData[9])
            }
        #return json.dumps(dataj)

        #************************************
        ''' Print Values on screen '''
        #************************************
        print("\n Lab: ", self.lab)
        print(" Measurement type: ", self.measType)
        print(" BM sensor: ", self.BMsensor)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.1f} deg C".format(self.sensData[6]))
        print(" Pressure = {0:0.1f} hPa".format(self.sensData[7]))
        print(" Humidity = {0:0.1f} %".format(self.sensData[8]))
        print(" Dew Point = {0:0.1f} deg C".format(self.sensData[9]),"\n")
        return dataj

    #************************************
    ''' Read Sensor BMP180 '''
    #************************************
    def readSensors180(self):
        self.sensData.extend([self.lab, self.measType, self.BMsensor, self.ip, self.date, self.time])
        try:
             sensor = BMP085.BMP085()
             self.sensData.extend([sensor.read_temperature(),
                                  sensor.read_pressure() / 100])
             self.sensData.extend([sensor.read_altitude()])
             self.sensData.extend([sensor.read_sealevel_pressure()])
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.sensData.extend([0,0,0,0])

        dataj = {
            'lab' : self.sensData[0],
            'measType' : self.sensData[1],
            'BMsensor' : self.sensData[2],
            'IP' : self.sensData[3],
            'date' : self.sensData[4],
            'time' : self.sensData[5],
            'temperature' : '{0:0.1f}'.format(self.sensData[6]),
            'pressure' : '{0:0.1f}'.format(self.sensData[7]),
            'altitude' : '{0:0.1f}'.format(self.sensData[8]),
            'sealevel_pressure' : '{0:0.1f}'.format(self.sensData[9])
            }
        #return json.dumps(dataj)

        #************************************
        ''' Print Values on screen '''
        #************************************
        print("\n Lab: ", self.lab)
        print(" Measurement type: ", self.measType)
        print(" BM sensor: ", self.BMsensor)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.1f} deg C".format(self.sensData[6]))
        print(" Pressure = {0:0.1f} hPa".format(self.sensData[7]))
        print(" Altitude = {0:0.1f} m".format(self.sensData[8]))
        print(" Sealevel pressure = {0:0.1f} Pa".format(self.sensData[9]),"\n")
        return dataj
