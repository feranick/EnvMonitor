#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* EnvMonitor - Environmental Tracking with PM
* version: 20190307a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

#***************************************************
''' This is needed for installation through pip '''
#***************************************************
def EnvMonitor_PM():
    main()
#***************************************************

import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
from libEnvMonitor import *
from BMsensors import *
from PMsensor import *

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
    ''' Read from T/RH sensor '''
    #************************************
    trhSensor = TRHSensor(conf)
    if conf.BMsensor == 'BME280':
        sensData = trhSensor.readSensors280()
    elif conf.BMsensor == 'BMP180':
        sensData = trhSensor.readSensors180()
    
    #************************************
    ''' Read from PM sensor '''
    #************************************
    pms = PMSensor(pms_gpio)
    conc, conc_pcf, conc_ugm3, conc_aqi = pms.collect()
    pms.printUI()
    #sensData.extend([conc, conc_aqi])
    pms.cleanup()
    sensData['PM2.5_particles_L'] : '{0:0.2f}'.format(conc)
    sensData['aqi'] : '{0:0d}'.format(int(conc_aqi))
    
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
