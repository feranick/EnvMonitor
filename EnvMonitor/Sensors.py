#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
************************************************************
* EnvMonitor - Sensors
* version: 20210504a
* By: Nicola Ferralis <feranick@hotmail.com>
************************************************************
'''
#print(__doc__)
import time, math
from datetime import datetime
from libEnvMonitor import *
import board, busio, math

#************************************
# Class T/RH Sensor
#************************************
class TRHSensor:
    def __init__(self, config):
        self.sea_level_pressure = getBaromPress(config)
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
 
        # To initialise using the default address:
        if config.TPsensor == 'MCP9808':
            import adafruit_mcp9808
            self.sensor = adafruit_mcp9808.MCP9808(self.i2c)
            try:
                self.temperature = self.sensor.temperature
            except:
                self.failSafe()
            self.pressure = 0
            self.humidity = 1
            self.dewpoint = 0
            self.altitude = 0

        elif config.TPsensor == 'BME280':
            import adafruit_bme280
            self.sensor = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
            try:
                self.sensor.mode = adafruit_bme280.MODE_NORMAL
                self.sensor.standby_period = adafruit_bme280.STANDBY_TC_500
                self.sensor.iir_filter = adafruit_bme280.IIR_FILTER_X16
                self.sensor.overscan_pressure = adafruit_bme280.OVERSCAN_X16
                self.sensor.overscan_humidity = adafruit_bme280.OVERSCAN_X1
                self.sensor.overscan_temperature = adafruit_bme280.OVERSCAN_X2
                # The sensor will need a moment to gather initial readings
                time.sleep(1)
                self.pressure = self.sensor.pressure
                self.temperature = self.sensor.temperature
                self.pressure = self.sensor.pressure
                self.humidity = self.sensor.relative_humidity
                self.altitude = self.sensor.altitude
            except:
                self.failSafe()

        elif config.TPsensor == 'SCD30':
            import adafruit_scd30
            try:
                self.sensor = adafruit_scd30.SCD30(self.i2c)
                self.pressure = self.sea_level_pressure
                #print(" Temperature offset:", self.sensor.temperature_offset)
                #print(" Measurement interval:", self.sensor.measurement_interval)
                #print(" Self-calibration enabled:", self.sensor.self_calibration_enabled)
                #print(" Ambient Pressure:", self.sensor.ambient_pressure)
                #print(" Altitude:", self.sensor.altitude, "meters above sea level")
                #print(" Forced recalibration reference:", self.sensor.forced_recalibration_reference)
                while True:
                    if self.sensor.data_available:
                        self.temperature = self.sensor.temperature
                        self.pressure = self.sensor.ambient_pressure
                        self.humidity = self.sensor.relative_humidity
                        self.altitude = self.sensor.altitude
                        self.CO2 = self.sensor.CO2
                        break
                    time.sleep(0.5)
            except:
                self.failSafe()
                
        elif config.TPsensor == 'BME180':
            import Adafruit_BMP.BMP085 as BMP085
            import RPi.GPIO as GPIO
            try:
                sensor = BMP085.BMP085()
                self.temperature = sensor.read_temperature()
                self.pressure = sensor.read_pressure() / 100
                self.altitude = sensor.read_altitude()
            except:
                self.failSafe()
            self.humidity = 0
                    
        self.sealevel = self.sea_level_pressure
        self.dewpoint = dewPointRH(self.temperature, self.humidity, Pws(self.temperature, self.humidity))
        self.absHum = absHumidity(self.temperature,self.humidity, Pws(self.temperature,self.humidity))
        
    def failSafe(self):
        print("\n T/RH/P SENSOR NOT CONNECTED ")
        self.sensor = 0
        self.temperature = 0
        self.pressure = 0
        self.humidity = 1
        self.altitude = 0
        self.CO2 = 0
        self.sealevel = self.sea_level_pressure
        
#************************************
# Class Gas Sensor
#************************************
class SGP30:
    def __init__(self, config, absHumidity):
        import adafruit_sgp30
        print(" Gas Sensor Warming up, please wait...\n")
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        # To initialise using the default address:
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        
        #print("SGP30 serial #", [hex(i) for i in self.sgp30.serial])
        self.sgp30.iaq_init()
        
        # Original baseline
        #self.sgp30.set_iaq_baseline(0x8973, 0x8AAE)
       
        # Dynamic baseline
        #print("**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x" % (config.eCO2_baseline, config.TVOC_baseline))
        self.sgp30.set_iaq_baseline(config.eCO2_baseline, config.TVOC_baseline)
        
        # Apply humidity correction
        self.sgp30.set_iaq_humidity(absHumidity)
        elapsed_sec = 0
    
        #print("eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
        while True:
            #print("eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
            time.sleep(1)
            elapsed_sec += 1
            if elapsed_sec > 10:
                #elapsed_sec = 0
                print(" eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
            if elapsed_sec > 15:
                print(" eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
                print(" **** Baseline values: eCO2 = 0x%x, TVOC = 0x%x" % (self.sgp30.baseline_eCO2, self.sgp30.baseline_TVOC))
                self.sgp30.set_iaq_baseline(self.sgp30.baseline_eCO2, self.sgp30.baseline_TVOC)
                break
        
    def readGasSensor(self):
        try:
            self.CO2 = self.sgp30.eCO2
            self.TVOC = self.sgp30.TVOC
        except:
            print("\n GAS SENSOR NOT CONNECTED ")
            self.CO2 = 0
            self.TVOC = 0
        self.baseline_eCO2 = self.sgp30.baseline_eCO2
        self.baseline_TVOC = self.sgp30.baseline_TVOC
        
