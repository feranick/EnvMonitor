#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
* EnvMonNest - Control Nest Thermostat based on Air Quality
#* version: 2021015b
* By: Nicola Ferralis <feranick@hotmail.com>
***********************************************************
'''
#print(__doc__)

#***************************************************
''' This is needed for installation through pip '''
#***************************************************
def EnvMonNest():
    main()
#***************************************************

import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
import numpy as np
import pandas as pd
from libEnvMonitor import *
from GNestAccess import *

#************************************
# Main - Scheduler
#************************************
def main():
    config = Configuration()
    s = sched.scheduler(time.time, time.sleep)
    
    gnest = GoogleNest()
    gnest.getToken()
    gnest.dev, tmp = gnest.getDevices(0)
    
    gnest = 0
    while True:
        s.enter(config.sleepSeconds, config.priority, runAcq, (gnest,))
        s.run()

#************************************
# Run Acquistion
#************************************
def runAcq(gnest):
    config = Configuration()
    jsonData={}
    conn = SubMongoDB(json.dumps(jsonData), config)
    
    date = time.strftime("%Y%m%d")
    entry = conn.getData(date, config.lab)[-1]
    
    print("\n Lab: ", config.lab)
    print(" Date: ", entry['date'])
    print(" Time: ", entry['time'])
    print(" Temperature = {0:0.1f} deg C".format(entry['temperature']))
    print(" Pressure = {0:0.1f} hPa".format(entry['pressure']))
    print(" Humidity = {0:0.1f} %".format(entry['humidity']))
    print(" Dew Point = {0:0.1f} deg C".format(entry['dewpoint']))
    print(" CO2 = {0:0.1f} ppm".format(entry['CO2']))
    print(" Total Volatile Organic Content = {0:0.1f} ppb".format(entry['TVOC']),"\n")
    
    print(config.minCO2, config.maxCO2)
    
    if CO2 > config.maxCO2 and gnest.getFanTrait(0) is not "ON":
        print(" Run Fan!", CO2)
        gnest.setFanON(gnest.dev)
    if CO2 < config.minCO2:
        print(" STOP Fan!", CO2)
        gnest.setFanOFF(gnest.dev)
    '''

#************************************
# Main initialization routine
#************************************
if __name__ == "__main__":
    sys.exit(main())
