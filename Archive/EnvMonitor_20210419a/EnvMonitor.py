#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
* EnvMonitor - Environmental Tracking
# version: 20210416a
* By: Nicola Ferralis <feranick@hotmail.com>
***********************************************************
'''
#print(__doc__)

#***************************************************
# This is needed for installation through pip
#***************************************************
def EnvMonitor():
    main()
#***************************************************

import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
import numpy as np
import pandas as pd
from libEnvMonitor import *

#************************************
# Main - Scheduler
#************************************
def main():
    config = Configuration()
    s = sched.scheduler(time.time, time.sleep)
    while True:
        s.enter(config.sleepSeconds, config.priority, runAcq)
        s.run()

#************************************
# Run Acquistion
#************************************
def runAcq():
    config = Configuration()
    
    if config.TPsensor == 'BMP180':
        from BMP180sensors import TRHSensor
    else:
        from Tsensors import TRHSensor
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
    absHum = absHumidity(temperature,humidity, Pws(temperature,humidity))
    
    if config.Gassensor == 'SGP30':
        from Gassensors import GasSensor
        GSens = GasSensor(config, absHum)
        GSens.readGasSensor()
        CO2 = GSens.CO2
        TVOC = GSens.TVOC
    else:
        CO2 = 0
        TVOC = 0

    ip = getIP()
    date = time.strftime("%Y%m%d")
    time1 = time.strftime("%H:%M:%S")
        
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
            'eCO2_baseline' : hex(GSens.baseline_eCO2),
            'TVOC_baseline' : hex(GSens.baseline_TVOC),
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
        print(" Total Volatile Organic Content = {0:0.1f} ppb\n".format(TVOC))
      
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

#************************************
# Main initialization routine
#************************************
if __name__ == "__main__":
    sys.exit(main())
