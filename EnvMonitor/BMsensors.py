#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - BMsensors
* version: 20190306a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)
import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
#import numpy as np
from libEnvMonitor import *
from Adafruit_BME280 import *
import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO

#************************************
''' Class T/RH Sensor '''
#************************************
class TRHSensor:
    def __init__(self, config):
        self.config = config
        self.date = time.strftime("%Y%m%d")
        self.time = time.strftime("%H:%M:%S")
        self.ip = getIP()
    
    #************************************
    ''' Read Sensor BME280 '''
    #************************************
    def readSensors280(self):
        try:
             sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
             self.temperature = sensor.read_temperature()
             self.pressure = sensor.read_pressure() / 100
             self.humidity = sensor.read_humidity()
             self.dewpoint = sensor.read_dewpoint()
        except:
             print("\n SENSOR NOT CONNECTED ")
             self.temperature = 0
             self.pressure = 0
             self.humidity = 0
             self.dewpoint = 0
        
        jsonData = {
            'lab' : self.config.lab,
            'measType' : self.config.measType,
            'BMsensor' : self.config.BMsensor,
            'IP' : self.ip,
            'date' : self.date,
            'time' : self.time,
            'temperature' : self.temperature,
            'pressure' : self.pressure,
            'humidity' : self.humidity,
            'dewpoint' : self.dewpoint,
            }
    
        #************************************
        ''' Print Values on screen '''
        #************************************
        if self.config.verbose:
            print("\n Lab: ", self.config.lab)
            print(" Measurement type: ", self.config.measType)
            print(" BM sensor: ", self.config.BMsensor)
            print(" IP: ", self.ip)
            print(" Date: ", self.date)
            print(" Time: ", self.time)
            print(" Temperature = {0:0.1f} deg C".format(self.temperature))
            print(" Pressure = {0:0.1f} hPa".format(self.pressure))
            print(" Humidity = {0:0.1f} %".format(self.humidity))
            print(" Dew Point = {0:0.1f} deg C".format(self.dewpoint),"\n")
        
        return jsonData

    #************************************
    ''' Read Sensor BMP180 '''
    #************************************
    def readSensors180(self):
        try:
             sensor = BMP085.BMP085()
             self.temperature = sensor.read_temperature()
             self.pressure = sensor.read_pressure() / 100
             self.altitude = sensor.read_altitude()
             self.sealevel = sensor.read_sealevel_pressure() / 100
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.temperature = 0
            self.pressure = 0
            self.altitude = 0
            self.sealevel = 0
        
        jsonData = {
            'lab' : self.config.lab,
            'measType' : self.config.measType,
            'BMsensor' : self.config.BMsensor,
            'IP' : self.ip,
            'date' : self.date,
            'time' : self.time,
            'temperature' : self.temperature,
            'pressure' : self.pressure,
            'altitude' : self.altitude,
            'sealevel_pressure' : self.sealevel,
            }

        #************************************
        ''' Print Values on screen '''
        #************************************
        if self.config.verbose:
            print("\n Lab: ", self.config.lab)
            print(" Measurement type: ", self.config.measType)
            print(" BM sensor: ", self.config.BMsensor)
            print(" IP: ", self.ip)
            print(" Date: ", self.date)
            print(" Time: ", self.time)
            print(" Temperature = {0:0.1f} deg C".format(self.temperature))
            print(" Pressure = {0:0.1f} hPa".format(self.pressure))
            print(" Altitude = {0:0.1f} m".format(self.altitude))
            print(" Sealevel pressure = {0:0.1f} hPa".format(self.sealevel),"\n")
        return jsonData
