#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GetEnvData
* version: 20190304a
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
from EnvMonitor import *

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
                                   "tphif:", ["temperature", "pressure", "humidity", "id", "file"])
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
            conn.getByType("temperature")
        if o in ("-p" , "--pressure"):
            conn.getByType("pressure")
        if o in ("-h" , "--humidity"):
            conn.getByType("humidity")
        if o in ("-i" , "--id"):
            conn.getById(sys.argv[2])
        if o in ("-f" , "--file"):
            conn.getByFile(sys.argv[2])
    #except:
    #    print("\n Getting entry from database failed!\n")

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
