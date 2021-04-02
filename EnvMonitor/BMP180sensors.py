#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - BMP Sensors
* version: 20210402a
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
        if config.TPsensor == 'BME180':
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
            self.humidity = 0
            self.dewpoint = 0
        
        ### Deprecated as BMP280 uses CircuitPython now.
        elif config.TPsensor == 'BME280':
            try:
                BME280_OSAMPLE_8 = 4
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
            self.altitude = 0
            self.sealevel = 0
