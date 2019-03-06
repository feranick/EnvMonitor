#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GetEnvData
* version: 20190306b
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

#***************************************************
''' This is needed for installation through pip '''
#***************************************************
def GetEnvData():
    main()
#***************************************************

import configparser, logging, sys, math
import json, os.path, time, base64, getopt
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from libEnvMonitor import *
import matplotlib.pyplot as plt

#************************************
''' Main '''
#************************************
def main():
    conf = Configuration()
    if os.path.isfile(conf.configFile) is False:
        print("Configuration file does not exist: Creating one.")
        conf.createConfig()
    conf.readConfig(conf.configFile)
    path = conf.dataFolder
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "tphwalsdif:", ["temperature", "pressure", "humidity", "dewpoint", "altitude", "sealevel", "all","delete", "id", "file"])
    except:
        usage()
        sys.exit(2)

    if opts == []:
        usage()
        sys.exit(2)

    #************************************
    ''' Push to MongoDB '''
    #************************************
    try:
        for o, a in opts:
            jsonData={}
            conn = SubMongoDB(json.dumps(jsonData), conf)
            if o in ("-t" , "--temperature"):
                plotSingleData(conn.getByType("temperature"), "temperature")
            if o in ("-p" , "--pressure"):
                plotSingleData(conn.getByType("pressure"), "pressure")
        
            if o in ("-h" , "--humidity"):
                plotSingleData(conn.getByType("humidity"), "humidity")
            if o in ("-w" , "--dewpoint"):
                plotSingleData(conn.getByType("dewpoint"), "dewpoint")

            if o in ("-l" , "--altitude"):
                plotSingleData(conn.getByType("altitude"), "altitude")
            if o in ("-s" , "--sealevel"):
                plotSingleData(conn.getByType("sealevel"), "sealevel pressure")

            if o in ("-a" , "--all"):
                entries = conn.getData()
                data = np.empty((0,4))
                for entry in entries:
                    data = np.vstack([data, [entry['time'],entry['temperature'], entry['pressure'], entry['humidity']]])
                labels =['time','temperature','pressure','humidity']
                plotMultiData(data, labels)

        if o in ("-d" , "--delete"):
            conn.deleteDB()
        '''
        if o in ("-i" , "--id"):
            data = conn.getById(sys.argv[2])
        if o in ("-f" , "--file"):
            data = conn.getByFile(sys.argv[2])
        '''
    except:
        print("\n Getting entry from database failed! Are you using the correct sensor?\n")


#************************************
''' Plot data '''
#************************************
def plotSingleData(data, type):
    x = data[:,1]
    y = np.around(data[:,2].astype(float), decimals=1)
    numTicks = int(len(y)/10)
    fig, ax1 = plt.subplots(1,1, figsize=(9,8))
    ax1.plot(x,y, label='EnvMon')
    ax1.set_title('EnvMonitor')
    ax1.set_xlabel('time')
    ax1.set_ylabel(type)
    ax1.set_xticks(x[::numTicks])
    ax1.set_xticklabels(x[::numTicks], rotation=45)
    plt.show()
    plt.close()

def plotMultiData(data, labels):
    x = data[:,0]
    y1 = data[:,1].astype(float)
    y2 = data[:,2].astype(float)
    y3 = data[:,3].astype(float)
    numTicks = int(len(x)/10)
    fig, (ax1, ax2, ax3) = plt.subplots(3,1, figsize=(9,8))
    ax1.plot(x,y1, label='EnvMon')
    ax1.set_title('EnvMonitor')
    ax1.set_ylabel(labels[1])
    ax1.set_xticks(x[::numTicks])
    ax1.set_xticklabels([])
    ax2.plot(x,y2, label='EnvMon')
    ax2.set_ylabel(labels[2])
    ax2.set_xticklabels([])
    ax3.set_xticklabels([])
    ax3.plot(x,y3, label='EnvMon')
    ax3.set_xlabel(labels[0])
    ax3.set_ylabel(labels[3])
    ax3.set_xticks(x[::numTicks])
    ax3.set_xticklabels(x[::numTicks], rotation=45)

    plt.show()
    plt.close()

#************************************
''' Lists the program usage '''
#************************************
def usage():
    print('\n Usage:\n')
    print(' Query all data for temperature/pressure/humidity:')
    print('  python3 GetEnvData.py -t (or -p or -h)\n')
    print(' Query based on ID:')
    print('  python3 GetEnvData.py -i <ObjectId>\n')
    print(' Query based on file name:')
    print('  python3 GetEnvData.py -f <filename>\n')

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
