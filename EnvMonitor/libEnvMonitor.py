#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* libEnvMonitor - Environmental Tracking
* version: 20190305a
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
            print("\n Connecting to MongoDB: Authentication status = {0}\n".format(auth_status))
            return client
        except:
            print("\n Connecting to MongoDB: Unsuccessful\n")
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

    def getByType(self, type):
        client = self.connectDB()
        db = client[self.config.DbName]
        data = np.empty((0,3))
        for entry in db[self.config.DbName].find():
            #print(entry['date'], entry['time'], entry[type])
            data = np.vstack((data, [entry['date'], entry['time'], entry[type]]))
        return data

    def deleteDB(self):
        client = self.connectDB()
        db = client[self.config.DbName]
        i = 0
        for entry in db[self.config.DbName].find():
            db[self.config.DbName].delete_one({'_id': entry['_id']})
            i+=1
        print(" All",i,"entries for:",self.config.DbName, "deleted\n")

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
            'itemId' : '1',
            'BMsensor' : 'BME280',
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
            self.runSeconds = self.conf.getint('System','runSeconds')
            self.sleepSeconds = self.conf.getint('System','sleepSeconds')

            self.lab = self.instrumentationConfig['lab']
            self.name = self.instrumentationConfig['name']
            self.measType = self.instrumentationConfig['measType']
            #self.architecture = self.instrumentationConfig['architecture']
            self.itemId = self.instrumentationConfig['itemId']
            self.BMsensor = self.instrumentationConfig['BMsensor']
            
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
