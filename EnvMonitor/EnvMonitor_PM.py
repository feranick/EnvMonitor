#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking with PM
* version: 20190303b
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
from Adafruit_BME280 import *
import RPi.GPIO as GPIO

pms_gpio = 15  # (GPIO15, pin 10)

#************************************
''' Main - Scheduler '''
#************************************
def main():
    s = sched.scheduler(time.time, time.sleep)
    while True:
        conf = Configuration()
        if os.path.isfile(conf.configFile) is False:
            print("Configuration file does not exist: Creating one.")
            conf.createConfig()
        conf.readConfig(conf.configFile)
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
    sensData = trhSensor.readSensors()
    trhSensor.printUI()
    
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
            conn = SubMongoDB(json.dumps(sensData))
            #conn.checkCreateLotDM(sub)
            conn.pushToMongoDB()
    except:
        print("\n Submission to database failed!\n")

#************************************
''' Class T/RH Sensor '''
#************************************
class TRHSensor:
    def __init__(self, config):
        #config = Configuration()
        #config.readConfig(config.configFile)
        self.date = time.strftime("%Y%m%d")
        self.time = time.strftime("%H:%M:%S")
        self.sensData = []
        self.ip = getIP()
        self.lab = config.lab
        self.measType = config.measType
    
    #************************************
    ''' Read Sensors '''
    #************************************
    def readSensors(self):
        self.sensData.extend([self.lab, self.measType, self.ip, self.date, self.time])
        try:
            sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
            self.sensData.extend([sensor.read_temperature(),
                                  sensor.read_pressure() / 100,
                                  sensor.read_humidity()])
            dataj = {
            'lab' : self.sensData[0],
            'measType' : self.sensData[1],
            'IP' : self.sensData[2],
            'date' : self.sensData[3],
            'time' : self.sensData[4],
            'temperature' : '{0:0.1f}'.format(self.sensData[5]),
            'pressure' : '{0:0.1f}'.format(self.sensData[6]),
            'humidity' : '{0:0.1f}'.format(self.sensData[7]),
            }
        except:
            print("\n SENSOR NOT CONNECTED ")
            dataj = self.sensData.extend([0.0,0.0,0.0])
        #return json.dumps(dataj)
        return dataj
        
    #************************************
    ''' Print Values on screen '''
    #************************************
    def printUI(self):
        print("\n Lab: ", self.lab)
        print(" Measurement type: ", self.measType)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.1f} deg C".format(self.sensData[5]))
        print(" Pressure = {0:0.1f} hPa".format(self.sensData[6]))
        print(" Humidity = {0:0.1f} %".format(self.sensData[7]),"\n")

#************************************
''' Class Particulate Sensor '''
#************************************
class PMSensor:
    '''
    A class to read a Shinyei PPD42NS Dust Sensor, e.g. as used
    in the Grove dust sensor.

    This code calculates the percentage of low pulse time and
    calibrated concentration in particles per 1/100th of a cubic
    foot at user chosen intervals.
    '''

    def __init__(self, gpio):
        try:
            import pigpio
        except:
            self.GPIO = None
        else:
            self.GPIO = pigpio
        
        self.collectionTime = 30
        self.pi = pigpio.pi()
        self.gpio = gpio
        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0
        self.ratio = 0
        
        self.pi.set_mode(gpio, pigpio.INPUT)
        self._cb = self.pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def collect(self):
        runTime = time.time()
        while time.time() - runTime <= self.collectionTime:
            print(" Waiting",int(time.time() - runTime),
                  "/",int(self.collectionTime),"s for PM sensor...", end="\r")
        print("                                           ", "\r")
        self.read()
        return (self.conc, self.conc_pcf, self.conc_ugm3, self.conc_aqi)
    
    def read(self):
        interval = self._low_ticks + self._high_ticks
        if interval > 0:
            self.ratio = float(self._low_ticks)/float(interval)*100.0
        else:
            self.ratio = 0
        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0
        self.conc_pcf = 1.1*pow(self.ratio,3)-3.8*pow(self.ratio,2)+520*self.ratio+0.62
        self.conc = self.conc_pcf/0.2831685 # concentration in particles/L
        self.conc_ugm3 = self.pcf_to_ugm3(self.conc)
        self.conc_aqi = self.ugm3_to_aqi(self.conc_ugm3)
    
    def _cbf(self, gpio, level, tick):
        if self._start_tick is not None:
            ticks = self.GPIO.tickDiff(self._last_tick, tick)
            self._last_tick = tick
            if level == 0: # Falling edge.
                self._high_ticks = self._high_ticks + ticks
            elif level == 1: # Rising edge.
                self._low_ticks = self._low_ticks + ticks
            else: # timeout level, not used
                pass
        else:
            self._start_tick = tick
            self._last_tick = tick

    def pcf_to_ugm3(self, conc_pcf):
        '''
        Convert concentration of PM2.5 particles per 0.01 cubic feet to µg/ metre cubed
        this method outlined by Drexel University students (2009) and is an approximation
        does not contain correction factors for humidity and rain
        '''
        # Assume all particles are spherical, with a density of 1.65E12 µg/m3
        densitypm25 = 1.65 * math.pow(10, 12)
        
        # Assume the radius of a particle in the PM2.5 channel is .44 µm
        rpm25 = 0.44 * math.pow(10, -6)
        
        # Volume of a sphere = 4/3 * pi * radius^3
        volpm25 = (4/3) * math.pi * (rpm25**3)
        
        # mass = density * volume
        masspm25 = densitypm25 * volpm25
        
        # parts/m3 =  parts/foot3 * 3531.5
        # µg/m3 = parts/m3 * mass in µg
        conc_ugm3 = conc_pcf * 3531.5 * masspm25
        return conc_ugm3
    
    def ugm3_to_aqi(self, ugm3):
        '''
        Convert concentration of PM2.5 particles in µg/ metre cubed to the USA
        Environment Agency Air Quality Index - AQI
        https://en.wikipedia.org/wiki/Air_quality_index
        Computing_the_AQI
        https://goo.gl/biYDqq
        '''
        cbreakpointspm25 = [ [0.0, 12, 0, 50],\
                        [12.1, 35.4, 51, 100],\
                        [35.5, 55.4, 101, 150],\
                        [55.5, 150.4, 151, 200],\
                        [150.5, 250.4, 201, 300],\
                        [250.5, 350.4, 301, 400],\
                        [350.5, 500.4, 401, 500], ]
        C=ugm3
        if C > 500.4:
            aqi=500
        else:
           for breakpoint in cbreakpointspm25:
               if breakpoint[0] <= C <= breakpoint[1]:
                   Clow = breakpoint[0]
                   Chigh = breakpoint[1]
                   Ilow = breakpoint[2]
                   Ihigh = breakpoint[3]
                   aqi=(((Ihigh-Ilow)/(Chigh-Clow))*(C-Clow))+Ilow
        return aqi

    def printUI(self):
        print("\n Particulate Sensor for PM2.5:     \n  particles/L: {0:0.2f}".format(self.conc),
              "\n  particles/cu-ft: {0:0.2f}".format(self.conc_pcf),
              "\n  ug/m^3: {0:0.2f}".format(self.conc_ugm3),
              "\n  aqi: {0:0d}".format(int(self.conc_aqi)), "\n")

    def cleanup(self):
        self.pi.stop()

#************************************
''' Class Database '''
#************************************
class SubMongoDB:
    def __init__(self, jsonData, config):
        self.config = config
        #self.config = Configuration()
        #self.config.readConfig(self.config.configFile)
        if self.config.dataType == 0:
            self.jsonData = jsonData
        else:
            self.jsonData = json.loads(jsonData)

    def connectDB(self):
        client = MongoClient(self.config.DbHostname, int(self.config.DbPortNumber))
        auth_status = client[self.config.DbName].authenticate(self.config.DbUsername,self.config.DbPassword)
        print("\n Pushing to MongoDB: Authentication status = {0}".format(auth_status))
        return client

    def printAuthInfo(self):
        print(self.config.DbHostname)
        print(self.config.DbPortNumber)
        print(self.config.DbName)
        print(self.config.DbUsername)
        print(self.config.DbPassword)
    
    def pushToMongoDB(self):
        client = self.connectDB()
        db = client[self.config.DbName]
        try:
            db_entry = db.Measurement.insert_one(self.jsonData)
            print(" Data entry successful (id:",db_entry.inserted_id,")\n")
        except:
            print(" Data entry failed.\n")
    '''
    # View entry in DM page for substrate/device
    def checkCreateLotDM(self, deviceID):
        client = self.connectDB()
        db = client[self.config.DbName]
        #try:
        entry = db.Lot.find_one({'label':deviceID[:8]})
        if entry:
            #db.Lot.update_one({ '_id': entry['_id'] },{"$push": self.getArchConfig(deviceID, row, col)}, upsert=False)
            msg = " Data entry for this batch found in DM. Created substrate: "+deviceID
        else:
            print(" No data entry for this substrate found in DM. Creating new one...")
            jsonData = {'label' : deviceID[:8], 'date' : deviceID[2:8], 'description': '', 'notes': '', 'tags': [], 'substrates': [{'isCollapsed': False, 'label': deviceID, 'material': '', 'flex': False, 'area': '', 'layers': [], 'attachments': [], 'devices': [{'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}]}
            db_entry = db.Lot.insert_one(json.loads(json.dumps(jsonData)))
                #db.Lot.update_one({ '_id': db_entry.inserted_id },{"$push": self.getArchConfig(deviceID,row,col)}, upsert=False)
            msg = " Created batch: " + deviceID[:8] + " and device: "+deviceID
        print(msg)
    
        
        #except:
        #    print(" Connection with DM via Mongo cannot be established.")
    '''

    def getById(self, id):
        from bson.objectid import ObjectId
        client = self.connectDB()
        db = client[self.config.DbName]
        db_entry = db.EnvMon.find_one({"_id": ObjectId(id)})
        print("\n Restoring file: :",db_entry['file'][2:])
        with open(db_entry['file'][2:], "wb") as fh:
            fh.write(base64.b64decode(db_entry[self.config.headers[0]]))

    def getByFile(self, file):
        client = self.connectDB()
        db = client[self.config.DbName]
        db_entry = db.EnvMon.find_one({"file": "./"+file})
        print("\n Restoring file: :",db_entry['file'][2:])
        with open(db_entry['file'][2:], "wb") as fh:
            fh.write(base64.b64decode(db_entry[self.config.headers[0]]))

####################################################################
# Configuration
####################################################################
class Configuration():
    def __init__(self):
        self.home = str(Path.home())+"/"
        #self.home = str(Path.cwd())+"/"
        self.configFile = self.home+"EnvMonitor.ini"
        self.generalFolder = self.home+"EnvMonitor/"
        #Path(self.generalFolder).mkdir(parents=True, exist_ok=True)
        self.logFile = self.generalFolder+"EnvMonitor.log"
        self.conf = configparser.ConfigParser()
        self.conf.optionxform = str
    
    # Create configuration file
    def createConfig(self):
        try:
            self.defineSystem()
            self.defineInstrumentation()
            #self.defineData()
            self.defineConfDM()
            with open(self.configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in creating configuration file")

    # Hadrcoded default definitions for the confoguration file
    def defineSystem(self):
        self.conf['System'] = {
            'appVersion' : 0,
            'loggingLevel' : logging.INFO,
            'loggingFilename' : self.logFile,
            'dataFolder' : ".",
            'runSeconds' : 5,
            'sleepSeconds' : 1,
            }
    def defineInstrumentation(self):
        self.conf['Instrumentation'] = {
            'measType' : 'test',
            'lab' : 'test',
            'name' : 'test',
            'itemId' : '1'
            }
    '''
    # for images/binary
    def defineData(self):
        self.conf['Data'] = {
            'headers' : ['image'],
            'encoding' : 'base64.b64encode',
            'dataType' : 0,
            'ncols': [0,1],
            }
    
    # for text/ASCII
    def defineData(self):
        self.conf['Data'] = {
            'headers' : ['header0','header1'],
            'encoding' : 'text/ASCII',
            'dataType' : 1,
            'ncols': [0,1],
            }
    
    # for text/csv
    def defineData(self):
        self.conf['Data'] = {
            'headers' : ['X','Y'],
            'encoding' : 'text/CSV',
            'dataType' : 1,
            'ncols': [0,1],
            'extension' : 'txt',
            }
    '''
    def defineConfDM(self):
        self.conf['DM'] = {
            'DbHostname' : "my.site.com",
            'DbPortNumber' : "27017",
            'DbName' : "test",
            'DbUsername' : "user",
            'DbPassword' : "pwd",
            }

    # Read configuration file into usable variables
    def readConfig(self, configFile):
        self.createConfig()
        self.conf.read(configFile)
        self.sysConfig = self.conf['System']
        self.appVersion = self.sysConfig['appVersion']
        try:
            self.instrumentationConfig = self.conf['Instrumentation']
            #self.dataConfig = self.conf['Data']
            self.dmConfig = self.conf['DM']

            self.loggingLevel = self.sysConfig['loggingLevel']
            self.loggingFilename = self.sysConfig['loggingFilename']
            self.dataFolder = self.sysConfig['dataFolder']
            self.runSeconds = self.conf.getint('System','runSeconds')
            self.sleepSeconds = self.conf.getint('System','sleepSeconds')

            self.lab = self.instrumentationConfig['lab']
            self.name = self.instrumentationConfig['name']
            self.measType = self.instrumentationConfig['measType']
            #self.architecture = self.instrumentationConfig['architecture']
            self.itemId = self.instrumentationConfig['itemId']
            
            '''
            self.headers = eval(self.dataConfig['headers'])
            self.dataType = eval(self.dataConfig['dataType'])
            self.encoding = self.dataConfig['encoding']
            self.ncols = eval(self.dataConfig['ncols'])
            self.extension = self.dataConfig['extension']
            '''
            
            self.DbHostname = self.dmConfig['DbHostname']
            self.DbPortNumber = self.conf.getint('DM','DbPortNumber')
            self.DbName = self.dmConfig['DbName']
            self.DbUsername = self.dmConfig['DbUsername']
            self.DbPassword = self.dmConfig['DbPassword']
        
        except:
            print("Configuration file is for an earlier version of the software")
            oldConfigFile = str(os.path.splitext(configFile)[0] + "_" +\
                    str(datetime.now().strftime('%Y%m%d-%H%M%S'))+".ini")
            print("Old config file backup: ",oldConfigFile)
            os.rename(configFile, oldConfigFile )
            print("Creating a new config file.")
            self.createConfig()
            self.readConfig(configFile)

    # Save current parameters in configuration file
    def saveConfig(self, configFile):
        try:
            with open(configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in saving parameters")

#************************************
''' Get system IP '''
#************************************
def getIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
