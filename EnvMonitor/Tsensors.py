#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - MCP9808 Temperature
* version: 20210413a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)
import time, math
from datetime import datetime
from libEnvMonitor import *
import board, busio, math

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
            
        elif config.TPsensor == 'BME280':
            import adafruit_bme280
            self.sensor = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
            try:
                self.sensor.sea_level_pressure = config.SeaLevelPressure
                self.sensor.mode = adafruit_bme280.MODE_NORMAL
                self.sensor.standby_period = adafruit_bme280.STANDBY_TC_500
                self.sensor.iir_filter = adafruit_bme280.IIR_FILTER_X16
                self.sensor.overscan_pressure = adafruit_bme280.OVERSCAN_X16
                self.sensor.overscan_humidity = adafruit_bme280.OVERSCAN_X1
                self.sensor.overscan_temperature = adafruit_bme280.OVERSCAN_X2
                # The sensor will need a moment to gather initial readings
                time.sleep(1)
                self.temperature = self.sensor.temperature
                self.pressure = self.sensor.pressure
                self.humidity = self.sensor.relative_humidity
                self.altitude = self.sensor.altitude
                self.sealevel = self.sensor.sea_level_pressure
                self.dewpoint = dewPointRH(self.temperature, self.humidity, Pws(self.temperature, self.humidity))
            except:
                print("\n SENSOR NOT CONNECTED ")
                self.temperature = 0
                self.pressure = 0
                self.humidity = 0
                self.dewpoint = 0
                self.altitude = 0
                self.sealevel = 0
                
                
        
        
        
        
        
