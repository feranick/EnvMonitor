#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking - MCP9808 Temperature
* version: 20210401a
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
import adafruit_mcp9808

#************************************
''' Class T/RH Sensor '''
#************************************
class TRHSensor:
    def __init__(self, config):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
 
        # To initialise using the default address:
        self.mcp = adafruit_mcp9808.MCP9808(self.i2c)
        
        try:
            self.temperature = self.mcp.temperature
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.temperature = 0
        self.pressure = 0
        self.humidity = 0
        self.dewpoint = 0
        self.altitude = 0
        self.sealevel = 0
        