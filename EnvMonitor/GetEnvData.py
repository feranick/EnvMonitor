#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GetEnvData
* version: 20190305b
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
    
    #try:
    opts, args = getopt.getopt(sys.argv[1:],
                                   "tphdif:", ["temperature", "pressure", "humidity", "delete", "id", "file"])
    #except:
    #    usage()
    #    sys.exit(2)

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
            plotData(data, "temperature")
        if o in ("-p" , "--pressure"):
            data = conn.getByType("pressure")
            plotData(data, "pressure")
        if o in ("-h" , "--humidity"):
            data = conn.getByType("humidity")
            plotData(data, "humidity")
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
def plotData(data, type):
    '''
    learnFileRootNew = learnFileRoot
    if step == 1:
        start = 0
        learnFileRootNew = learnFileRoot + '_full-set'
        plt.title(learnFileRoot+'\nFull set (#'+str(M.shape[0])+')')
    else:
        start = random.randint(0,10)
        learnFileRootNew = learnFileRoot + '_partial-' + str(step) + '_start-' + str(start)
        plt.title(learnFileRootNew+'\nPartial Set (#'+str(M.shape[0])+'): every '+str(step)+' spectrum, start at: '+ str(start))

    print(' Plotting Training dataset in: ' + learnFileRootNew + '.png\n')
    
    for i in range(start,M.shape[0], step):
        plt.plot(En, M[i,:], label='Training data')
    '''
    
    plt.plot(data[:,1], data[:,2].astype(float), label='EnvMon')

    plt.xlabel('time')
    plt.ylabel(type)
    
    #plt.savefig(learnFileRootNew + '.png', dpi = 160, format = 'png')  # Save plot
    plt.gcf().autofmt_xdate()
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
