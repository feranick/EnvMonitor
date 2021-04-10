#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - MCP9808 Temperature
* version: 20210409a
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
                tmp = math.sqrt(self.temperature/self.humidity)
                self.dewpoint = 237.7 * tmp/(17.271-tmp)
            except:
                print("\n SENSOR NOT CONNECTED ")
                self.temperature = 0
                self.pressure = 0
                self.humidity = 0
                self.dewpoint = 0
                self.altitude = 0
                self.sealevel = 0
                
    def absHumidity(self, T1, RH):
        # https://www.hatchability.com/Vaisala.pdf
        T = T1 + 273.5
        
        ### Method 1 - accurate but comp. intensive
        Tc = 647.096       # in K
        Pc = 220639.128   # in hPa-7.85951783
        C1 = -7.85951783
        C2 = 1.84408259
        C3 = -11.7866497
        C4 = 22.6807411
        C5 = -15.9618719
        C6 = 1.80122502
        
        nu = 1 - T/Tc
        Pws = Pc * math.exp((Tc/T)*(C1*nu + C2*pow(nu, 1.5) + C3*pow(nu, 3) + C4*pow(nu, 3.5) + C5*pow(nu, 4) + C6*pow(nu, 7.5)))    #  in hPa
        
        ### Method 2 - less accurate but more efficient
        C = 2.16679    # in gK/J
        if T1 > -20 and T1 <= 50:
            A = 6.116441
            m = 7.591386
            Tn = 240.7263
        elif T1 > 50 and T1 <= 100:
            A = 6.004918
            m = 7.337936
            Tn = 229.3975
        
        self.RhA = C * (Pws * RH / 100) * 100/T
        print(self.RhA)
        
        Pws1 = (A * pow(10, (m*T1)/(T1+Tn)))
        self.RhA1 = C * (Pws1 * RH / 100) * 100/T
        print(self.RhA1)
        
        return self.RhA
                
        
        
        
        
        
