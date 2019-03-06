#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GetEnvData
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
                                   "tphwadif:", ["temperature", "pressure", "humidity", "dewpoint", "all","delete", "id", "file"])
    except:
        usage()
        sys.exit(2)

    if opts == []:
        usage()
        sys.exit(2)

    #************************************
    ''' Push to MongoDB '''
    #************************************
    #try:
    for o, a in opts:
        jsonData={}
        conn = SubMongoDB(json.dumps(jsonData), conf)
        if o in ("-t" , "--temperature"):
            data = conn.getByType("temperature")
            print(data)
            plotSingleData(data[:,1], data[:,2], "temperature")
        if o in ("-p" , "--pressure"):
            data = conn.getByType("pressure")
            plotData(data[:,1], np.around(data[:,2], decimals=1), "pressure")
        if o in ("-h" , "--humidity"):
            data = conn.getByType("humidity")
            plotData(data[:,1], np.around(data[:,2], decimals=1), "humidity")
        if o in ("-w" , "--dewpoint"):
            data = conn.getByType("dewpoint")
            plotData(data[:,1], np.around(data[:,2], decimals=1), "dewpoint")
        if o in ("-a" , "--all"):
            data = conn.getData()
            for entry in data:
                print(entry)
        if o in ("-d" , "--delete"):
            conn.deleteDB()
        '''
        if o in ("-i" , "--id"):
            data = conn.getById(sys.argv[2])
        if o in ("-f" , "--file"):
            data = conn.getByFile(sys.argv[2])
        '''
    #except:
    #    print("\n Getting entry from database failed!\n")

#************************************
''' Plot data '''
#************************************
def plotSingleData(x, y, type):
    numTicks = int(len(y)/10)
    fig, ax1 = plt.subplots(1,1, figsize=(9,8))
    ax1.plot(x,y, label='EnvMon')
    ax1.set_title(type)
    ax1.set_xlabel('time')
    ax1.set_ylabel(type)
    ax1.set_xticks(x[::numTicks])
    ax1.set_xticklabels(x[::numTicks], rotation=45)

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
