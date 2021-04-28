#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
* EnvMonitorNest - Environmental Tracking with Nest data
# version: 20210428a
* By: Nicola Ferralis <feranick@hotmail.com>
***********************************************************
'''
#print(__doc__)

#***************************************************
# This is needed for installation through pip
#***************************************************
def EnvMonitorNest():
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
from Sensors import TRHSensor

#************************************
# Main - Scheduler
#************************************
def main():
    config = Configuration()
    s = sched.scheduler(time.time, time.sleep)
    
    gnest = GoogleNest()
    gnest.getToken()
    gnest.dev, tmp = gnest.getDevices(0)
    
    while True:
        s.enter(config.sleepSeconds, config.priority, runAcq,(gnest,))
        s.run()

#************************************
# Run Acquistion
#************************************
def runAcq(gnest):
    config = Configuration()
        
    #************************************
    ''' NEW: Read from sensors '''
    #************************************
    trhSensor = TRHSensor(config)
   
    temperature = trhSensor.temperature
    pressure = trhSensor.pressure
    humidity = trhSensor.humidity
    dewpoint = trhSensor.dewpoint
    altitude = trhSensor.altitude
    sealevel = trhSensor.sealevel
    absHum = trhSensor.absHum
    
    if config.Gassensor == 'SCD30':
        CO2 = trhSensor.CO2
        TVOC = 0
        baseline_eCO2 = 0
        baseline_TVOC = 0
    elif config.Gassensor == 'SGP30':
        from Sensors import SGP30
        GSens = SGP30(config, absHum)
        GSens.readGasSensor()
        CO2 = GSens.CO2
        TVOC = GSens.TVOC
        baseline_eCO2 = hex(GSens.baseline_eCO2)
        baseline_TVOC = hex(GSens.baseline_TVOC)
    else:
        CO2 = 0
        TVOC = 0
        baseline_eCO2 = 0
        baseline_TVOC = 0

    ip = getIP()
    date = time.strftime("%Y%m%d")
    time1 = time.strftime("%H:%M:%S")
    
    gnest.getDeviceStats(gnest.dev)
        
    sensData = {
            'lab' : config.lab,
            'name' : config.name,
            'measType' : config.measType,
            'TPsensor' : config.TPsensor,
            'Gassensor' : config.Gassensor,
            'IP' : ip,
            'date' : date,
            'time' : time1,
            'temperature' : temperature,
            'pressure' : pressure,
            'humidity' : humidity,
            'dewpoint' : dewpoint,
            'altitude' : altitude,
            'sealevel' : sealevel,
            'CO2' : CO2,
            'TVOC' : TVOC,
            'eCO2_baseline' : baseline_eCO2,
            'TVOC_baseline' : baseline_TVOC,
            'NestFanStatus' : gnest.fanStatus,
            'NestTemperature' : gnest.temperature,
            'NestHumidity' : gnest.humidity,
            }
    
    #************************************
    # Print Values on screen
    #************************************
    if config.verbose:
        print("\n Lab: ", config.lab)
        print(" Name: ", config.name)
        print(" Measurement type: ", config.measType)
        print(" IP: ", ip)
        print(" TP sensor: ", config.TPsensor)
        print(" Gas sensor: ", config.Gassensor)
        print(" Date: ", date)
        print(" Time: ", time1)
        print(" Temperature = {0:0.1f} deg C".format(temperature))
        print(" Pressure = {0:0.1f} hPa".format(pressure))
        print(" Humidity = {0:0.1f} %".format(humidity))
        print(" Dew Point = {0:0.1f} deg C".format(dewpoint))
        print(" Altitude = {0:0.1f} m".format(altitude))
        print(" Sealevel pressure = {0:0.1f} hPa".format(sealevel),)
        print(" CO2 = {0:0.1f} ppm".format(CO2))
        print(" Total Volatile Organic Content = {0:0.1f} ppb".format(TVOC))
        print(" Nest Fan:",gnest.fanStatus,"\n")
      
    if config.saveMongoDB:
        try:
            conn = SubMongoDB(json.dumps(sensData),config)
            #conn.checkCreateLotDM(sub)
            conn.pushToMongoDB()
        except:
            print("\n Submission to database failed!")
    if config.saveCSV:
        try:
            df = pd.DataFrame(sensData, index=[0])
            if not os.path.exists(config.CSVfile):
                df.to_csv(config.CSVfile, mode="a", header=True)
            else:
                df.to_csv(config.CSVfile, mode="a", header=False)
            print("\n Saved in "+config.CSVfile)
        except:
            print("\n Saving to CSV failed!")
            
    diffTime = time.time()-gnest.time
    if diffTime > 3000:
        gnest.refreshToken()
        gnest.time = time.time()

#************************************
# Main initialization routine
#************************************
if __name__ == "__main__":
    sys.exit(main())
