#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
***********************************************************
* GetEnvData
* version: 20210423a
* By: Nicola Ferralis <feranick@hotmail.com>
***********************************************************
'''
print(__doc__)

#***************************************************
# This is needed for installation through pip
#***************************************************
def GetEnvData():
    main()
#***************************************************

import configparser, logging, sys, math
import json, os.path, time, base64, getopt
from pathlib import Path
from datetime import datetime
from libEnvMonitor import *

#************************************
# Main
#************************************
def main():
    conf = Configuration()
    path = conf.dataFolder
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "tprwhscoabmdlif:", ["temperature", "pressure", "humidity", "dewpoint", "altitude", "sealevel", "co2",
            "tvoc", "all", "mobile", "backup", "delete", "list", "id", "file"])
    except:
        usage()
        sys.exit(2)

    if opts == []:
        usage()
        sys.exit(2)

    #************************************
    # Push to MongoDB
    #************************************
    if len(sys.argv) == 4:
        lab = sys.argv[3]
        date = sys.argv[2]
    elif len(sys.argv) == 3:
        lab = ""
        date = sys.argv[2]
    else:
        lab = ""
        date = ""
        
    #try:
    for o, a in opts:
        jsonData={}
        conn = SubMongoDB(json.dumps(jsonData), conf)
            
        if o in ("-t" , "--temperature"):
            plotSingleData(conn.getByType("temperature", date), "temperature")
        if o in ("-p" , "--pressure"):
            plotSingleData(conn.getByType("pressure", date), "pressure")
        if o in ("-r" , "--humidity"):
            plotSingleData(conn.getByType("humidity", date), "humidity")
        if o in ("-w" , "--dewpoint"):
            plotSingleData(conn.getByType("dewpoint", date), "dewpoint")
        if o in ("-h" , "--altitude"):
            plotSingleData(conn.getByType("altitude", date), "altitude")
        if o in ("-s" , "--sealevel"):
            plotSingleData(conn.getByType("sealevel", date), "sealevel pressure")
        if o in ("-c" , "--co2"):
            plotSingleData(conn.getByType("CO2", date), "CO2")
        if o in ("-o" , "--tvoc"):
            plotSingleData(conn.getByType("TVOC", date), "TVOC")
        
        if o in ("-a" , "--all"):
            displayAllData(conn, date, lab)
        
        if o in ("-m" , "--mobile"):
            displayDataMobile(conn, date, lab)
        
        if o in ("-b" , "--backup"):
            file = str(os.path.splitext(conf.CSVfile)[0]+ "-"+lab+"-backup_" +\
                str(date)+".csv")
            conn.backupDB(date, lab, file)
            print("\n Data saved in:",file,"\n")
        
        if o in ("-d" , "--delete"):
            yN = input("Are you sure (y/N)? ")
            if yN == "y":
                conn.deleteDB(date, lab)
        
        if o in ("-l", "--list"):
            conn.getDatesAvailable()
        
    #except:
    #    print("\n No entry in database\n")

#************************************
# Get data from database
#************************************
def displayAllData(conn, date, lab):
    import pandas as pd
    import numpy as np
    entries = conn.getData(date, lab)
    data = entries[['date', 'time', 'temperature', 'pressure', 'humidity', 'CO2', 'TVOC']].to_numpy()
    labels =['date', 'time','temperature','pressure','humidity','CO2','TVOC']
    plotMultiData(data, labels, lab)
    #plotMultiData2(entries, lab)
    
def displayDataMobile(conn, date, lab):
    entries = conn.getData(date, lab).iloc[-1]
    print("\n Last measurement:")
    print("\n Lab: ", entries['lab'])
    print(" Date: ", entries['date'])
    print(" Time: ", entries['time'])
    print(" Temperature = {0:0.1f} deg C".format(entries['temperature']))
    print(" Pressure = {0:0.1f} hPa".format(entries['pressure']))
    print(" Humidity = {0:0.1f} %".format(entries['humidity']))
    print(" Dew Point = {0:0.1f} deg C".format(entries['dewpoint']))
    print("\033[1m CO2 = {0:0.1f} ppm".format(entries['CO2']))
    print(" Total Volatile Organic Content = {0:0.1f} ppb\033[0m\n".format(entries['TVOC']))

#************************************
# Plot data
#************************************
def plotSingleData(data, type):
    import matplotlib.pyplot as plt
    import numpy as np
    date = data[-1,0]
    x = data[:,1]
    y = np.around(data[:,2].astype(float), decimals=1)
    if int(len(x)) <10:
        numTicks = int(len(x))
    else:
        numTicks = int(len(x)/10)
    fig, ax1 = plt.subplots(1,1, figsize=(9,8))
    ax1.plot(x,y, label='EnvMon')

    ax1.set_title('EnvMonitor: '+data[-1,0])
    ax1.set_xlabel('time')
    ax1.set_ylabel(type)
    ax1.set_xticks(x[::numTicks])
    ax1.set_xticklabels(x[::numTicks], rotation=45)
    plt.show()
    plt.close()

def plotMultiData(data, labels, lab):
    import matplotlib.pyplot as plt
    import numpy as np
    x = data[:,1]
    #x = np.vectorize(convertTime)(x)
    
    y1 = data[:,2].astype(float)
    #y2 = data[:,3].astype(float)
    y2 = data[:,4].astype(float)
    y3 = data[:,5].astype(float)
    y4 = data[:,6].astype(float)
    if int(len(x)) <10:
        numTicks = int(len(x))
    else:
        numTicks = int(len(x)/10)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1, figsize=(9,10))
    ax1.plot(x,y1, label='EnvMon')
    ax1.set_title('EnvMonitor: '+data[-1,0]+'  '+lab)
    ax1.set_ylabel(labels[2])
    ax1.set_xticks(x[::numTicks])
    ax1.set_xticklabels([])
    
    '''
    ax2.plot(x,y2, label='EnvMon')
    ax2.set_ylabel(labels[3])
    ax2.set_xticks(x[::numTicks])
    ax2.set_xticklabels([])
    '''
    
    ax2.plot(x,y2, label='EnvMon')
    ax2.set_ylabel(labels[4])
    ax2.set_xticks(x[::numTicks])
    ax2.set_xticklabels([])
    
    ax3.plot(x,y3, label='EnvMon')
    ax3.set_ylabel(labels[5])
    ax3.set_xticks(x[::numTicks])
    ax3.set_xticklabels([])
    
    ax4.plot(x,y4, label='EnvMon')
    ax4.set_ylabel(labels[6])
    ax4.set_xticks(x[::numTicks])
    ax4.set_xticklabels(x[::numTicks], rotation=45)
    ax4.set_xlabel(labels[1])

    plt.show()
    plt.close()
    
def plotMultiData2(entries, lab):
    import matplotlib.pyplot as plt
    
    plt.figure(1, figsize=(9,10))
    plt.subplot(4,1,1)
    entries.plot(kind='line',x='time',y='temperature',ax=plt.gca())
    plt.subplot(4,1,2)
    entries.plot(kind='line',x='time',y='humidity', ax=plt.gca())
    plt.subplot(4,1,3)
    entries.plot(kind='line',x='time',y='CO2', ax=plt.gca())
    plt.subplot(4,1,4)
    entries.plot(kind='line',x='time',y='TVOC', ax=plt.gca())
    plt.show()

#************************************
# Lists the program usage
#************************************
def usage():
    print(' Usage:\n')
    print(' Query data based on date (YYYYMMDD) for temperature/pressure/humidity:')
    print('  python3 GetEnvData.py -t (or -p or -h) <date>\n')
    print(' Query all data for temperature/pressure/humidity/co2/tvoc:')
    print('  python3 GetEnvData.py -t (or -p or -h or -c or -o)\n')
    print(' Query data based on date (YYYYMMDD) for all measurements:')
    print('  python3 GetEnvData.py -a <date>\n')
    print(' Query data based on date (YYYYMMDD) and lab for all measurements:')
    print('  python3 GetEnvData.py -a <date> <lab>\n')
    print(' Query all data for all measurements:')
    print('  python3 GetEnvData.py -a\n')
    print(' Query last measurement based on date (YYYYMMDD) for all measurements:')
    print('  python3 GetEnvData.py -m <date>\n')
    print(' Query last measurement for all measurements:')
    print('  python3 GetEnvData.py -m\n')
    print(' List dates and labs available with measurements:')
    print('  python3 GetEnvData.py -l\n')
    print(' Backup data on CSV based on date (YYYYMMDD) for all measurements:')
    print('  python3 GetEnvData.py -b <date>\n')
    print(' Backup data on CSV all data for all measurements:')
    print('  python3 GetEnvData.py -b\n')
    print(' Delete all data for all measurements:')
    print('  python3 GetEnvData.py -d\n')
    print(' Delete data based on date for all measurements:')
    print('  python3 GetEnvData.py -d <date>\n')
    '''
    print(' Query based on ID:')
    print('  python3 GetEnvData.py -i <ObjectId>\n')
    print(' Query based on file name:')
    print('  python3 GetEnvData.py -f <filename>\n')
    '''

#************************************
# Main initialization routine
#************************************
if __name__ == "__main__":
    sys.exit(main())
