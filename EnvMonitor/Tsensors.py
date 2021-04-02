#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - MCP9808 Temperature
* version: 20210401b
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)
import time
from datetime import datetime
from libEnvMonitor import *
import board, busio

#************************************
''' Class T/RH Sensor '''
#************************************
class TRHSensor:
    def __init__(self, config):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
 
        # To initialise using the default address:
        if config.TPsensor == 'MCP9808':
            import adafruit_mcp9808
            self.sensor = adafruit_mcp9808.MCP9808(self.i2c)
        elif config.TPsensor == 'BMP280':
            import adafruit_bmp280
            self.sensor = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c)
            self.sensor.sea_level_pressure = 1013.25
            self.sensor.mode = adafruit_bmp280.MODE_NORMAL
            self.sensor.standby_period = adafruit_bmp280.STANDBY_TC_500
            self.sensor.iir_filter = adafruit_bmp280.IIR_FILTER_X16
            self.sensor.overscan_pressure = adafruit_bmp280.OVERSCAN_X16
            self.sensor.overscan_temperature = adafruit_bmp280.OVERSCAN_X2
            # The sensor will need a moment to gather inital readings
            time.sleep(1)
        
        try:
            self.temperature = self.sensor.temperature
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.temperature = 0
        self.pressure = 0
        self.humidity = 0
        self.dewpoint = 0
        self.altitude = 0
        self.sealevel = 0
        
