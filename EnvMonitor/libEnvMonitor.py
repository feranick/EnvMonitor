#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* libEnvMonitor - Environmental Tracking
* version: 20210412a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, math, json, os.path, time, configparser, logging, sched
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
import numpy as np
import pandas as pd

#************************************
''' Class Database '''
#************************************
class SubMongoDB:
    def __init__(self, jsonData, config):
        self.config = config
        self.jsonData = json.loads(jsonData)

    def connectDB(self):
        try:
            client = MongoClient(self.config.DbHostname, int(self.config.DbPortNumber))
            auth_status = client[self.config.DbName].authenticate(self.config.DbUsername,self.config.DbPassword)
            if self.config.verbose:
                print(" Connecting to MongoDB: Authentication status = {0}\n".format(auth_status))
            return client
        except:
            print(" Connecting to MongoDB: Unsuccessful\n")
            return None

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
            db_entry = db[self.config.DbName].insert_one(self.jsonData)
            print(" Data entry successful (id:",db_entry.inserted_id,")")
        except:
            print(" Data entry failed.")

    def getById(self, id):
        from bson.objectid import ObjectId
        client = self.connectDB()
        db = client[self.config.DbName]
        db_entry = db[self.config.DbName].find_one({"_id": ObjectId(id)})
        print("\n Restoring file: :",db_entry['file'][2:])
        with open(db_entry['file'][2:], "wb") as fh:
            fh.write(base64.b64decode(db_entry[self.config.headers[0]]))
        return db_entry['file'][2:]

    def getByFile(self, file):
        client = self.connectDB()
        db = client[self.config.DbName]
        db_entry = db[self.config.DbName].find_one({"file": "./"+file})
        print("\n Restoring file: :",db_entry['file'][2:])
        with open(db_entry['file'][2:], "wb") as fh:
            fh.write(base64.b64decode(db_entry[self.config.headers[0]]))
        return db_entry['file'][2:]

    def getByType(self, type, date):
        client = self.connectDB()
        db = client[self.config.DbName]
        data = np.empty((0,3))
        for entry in db[self.config.DbName].find(date).sort([("time",1)]):
            #print(entry['date'], entry['time'], entry[type])
            data = np.vstack((data, [entry['date'], entry['time'], entry[type]]))
        return data
    
    def getData(self, date):
        client = self.connectDB()
        db = client[self.config.DbName]
        data = np.empty((0,1))
        for entry in db[self.config.DbName].find(date).sort([("time",1)]):
            data = np.append(data, entry)
        return data

    def deleteDB(self, date):
        client = self.connectDB()
        db = client[self.config.DbName]
        i = 0
        for entry in db[self.config.DbName].find(date):
            db[self.config.DbName].delete_one({'_id': entry['_id']})
            i+=1
        print(" All",i,"entries for:",self.config.DbName, "deleted\n")
        
    def backupDB(self, date, file):
            entries = self.getData(date)
            df = pd.DataFrame(entries[0], index=[0])
            for line in entries:
                #print(line)
                #print(list(line.items()))
                #obj = list(line.items())
                #print(np. array(obj))
            
                df_temp = pd.DataFrame(line, index=[0])
                df = df.append(df_temp)
            print(df)
            df.to_csv(file, mode="a", header=True)

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
        if os.path.isfile(self.configFile) is False:
            print("Configuration file does not exist: Creating one.")
            self.createConfig()
        self.readConfig(self.configFile)
    
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

    # Hardcoded default definitions for the configuration file
    def defineSystem(self):
        self.conf['System'] = {
            'appVersion' : 0,
            'loggingLevel' : logging.INFO,
            'loggingFilename' : self.logFile,
            'dataFolder' : '.',
            'verbose' : True,
            'runSeconds' : 5,
            'sleepSeconds' : 1,
            'saveCSV' : False,
            'saveMongoDB' : True,
            'CSVfile' : 'EnvMonitor.csv',
            }
    def defineInstrumentation(self):
        self.conf['Instrumentation'] = {
            'measType' : 'test',
            'lab' : 'test',
            'name' : 'test',
            'itemId' : '1',
            'TPsensor' : 'BME280',
            'SeaLevelPressure' : '1019.0',
            'Gassensor' : 'SGP30',
            'eCO2_baseline' : '0x93a7',
            'TVOC_baseline' : '0x9817',
            'resetBaseline' : False,
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
            'DbName' : "EnvMon",
            'DbUsername' : "user",
            'DbPassword' : "pwd",
            }

    # Read configuration file into usable variables
    def readConfig(self, configFile):
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
            self.verbose = self.conf.getboolean('System','verbose')
            self.runSeconds = self.conf.getint('System','runSeconds')
            self.sleepSeconds = self.conf.getint('System','sleepSeconds')
            self.saveCSV = self.conf.getboolean('System','saveCSV')
            self.saveMongoDB = self.conf.getboolean('System','saveMongoDB')
            self.CSVfile = self.sysConfig['CSVfile']
            
            self.lab = self.instrumentationConfig['lab']
            self.name = self.instrumentationConfig['name']
            self.measType = self.instrumentationConfig['measType']
            #self.architecture = self.instrumentationConfig['architecture']
            self.itemId = self.instrumentationConfig['itemId']
            self.TPsensor = self.instrumentationConfig['TPsensor']
            self.SeaLevelPressure = self.conf.getfloat('Instrumentation','SeaLevelPressure')
            self.Gassensor = self.instrumentationConfig['Gassensor']
            self.eCO2_baseline = int(self.conf.get('Instrumentation','eCO2_baseline'),16)
            self.TVOC_baseline = int(self.conf.get('Instrumentation','TVOC_baseline'),16)
            self.resetBaseline = self.conf.getboolean('Instrumentation','resetBaseline')
            
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

#************************************************
# Convert Relative Humidity to Absolute in g/m^3
#************************************************
def Pws(T1, RH):
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
    '''
    ### Method 2 - less accurate but more efficient
    if T1 > -20 and T1 <= 50:
        A = 6.116441
        m = 7.591386
        Tn = 240.7263
    elif T1 > 50 and T1 <= 100:
        A = 6.004918
        m = 7.337936
        Tn = 229.3975
        
    Pws1 = (A * pow(10, (m*T1)/(T1+Tn)))
    '''
    return Pws
        
def absHumidity(T1, RH, Pws):
    # https://www.hatchability.com/Vaisala.pdf
    T = T1 + 273.5
    C = 2.16679    # in gK/J
    RhA = C * (Pws * RH / 100) * 100/T
    return RhA
    
def dewPointRH(T1, RH, Pws):
    if T1 > -20 and T1 <= 50:
        A = 6.116441
        m = 7.591386
        Tn = 240.7263
    elif T1 > 50 and T1 <= 100:
        A = 6.004918
        m = 7.337936
        Tn = 229.3975
    
    Pw = Pws * RH / 100
    print(Pw)
    dew = Tn/((m/math.log10(Pw/A))-1)
    return dew
    
#************************************
# Get system IP
#************************************
def getIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
