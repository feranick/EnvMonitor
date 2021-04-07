#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - SGP30 Sensor
* version: 20210407a
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
import board, busio
import adafruit_sgp30

#************************************
''' Class Gas Sensor '''
#************************************
class GasSensor:
    def __init__(self, config):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        # To initialise using the default address:
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        
        #print("SGP30 serial #", [hex(i) for i in self.sgp30.serial])
        self.sgp30.iaq_init()
        
        # Original baseline
        #self.sgp30.set_iaq_baseline(0x8973, 0x8AAE)
       
        # Dynamic baseline
        print("\n**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x" % (config.eCO2_baseline, config.TVOC_baseline))
        self.sgp30.set_iaq_baseline(config.eCO2_baseline, config.TVOC_baseline)
       
        elapsed_sec = 0
    
        print("eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
        print("\nGas Sensor Warming up, please wait\n")
        while True:
            #print("eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
            time.sleep(1)
            elapsed_sec += 1
            if elapsed_sec > 10:
                #elapsed_sec = 0
                print("eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
            if elapsed_sec > 15:
                print("eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))
                print("**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x" % (self.sgp30.baseline_eCO2, self.sgp30.baseline_TVOC))
                self.sgp30.set_iaq_baseline(self.sgp30.baseline_eCO2, self.sgp30.baseline_TVOC)
                break
        
    def readGasSensor(self):
        try:
            self.CO2 = self.sgp30.eCO2
            self.TVOC = self.sgp30.TVOC
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.CO2 = 0
            self.TVOC = 0
        
        
