#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking
* version: 20190306a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

#***************************************************
''' This is needed for installation through pip '''
#***************************************************
def EnvMonitor():
    main()
#***************************************************

import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
import numpy as np
from libEnvMonitor import *
from BMsensors import *

#************************************
''' Main - Scheduler '''
#************************************
def main():
    s = sched.scheduler(time.time, time.sleep)
    conf = Configuration()
    if os.path.isfile(conf.configFile) is False:
        print("Configuration file does not exist: Creating one.")
        conf.createConfig()
    conf.readConfig(conf.configFile)
    while True:
        s.enter(conf.runSeconds, conf.sleepSeconds, runAcq)
        s.run()

#************************************
''' Run Acquistion '''
#************************************
def runAcq():
    conf = Configuration()
    conf.readConfig(conf.configFile)
    
    #************************************
    ''' NEW: Read from T/RH sensor '''
    #************************************
    trhSensor = TRHSensor(conf)
    if conf.BMsensor == 'BME280':
        sensData = trhSensor.readSensors280()
    elif conf.BMsensor == 'BMP180':
        sensData = trhSensor.readSensors180()
    try:
        conn = SubMongoDB(json.dumps(sensData),conf)
        #conn.checkCreateLotDM(sub)
        conn.pushToMongoDB()
    except:
        print("\n Submission to database failed!\n")

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
