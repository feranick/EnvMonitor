#!/usr/bin/env python3
'''
**********************************************************
* TMonitorLite - Environmental Tracking
* version: 20230919a
* By: Nicola Ferralis <feranick@hotmail.com>
***********************************************************
'''
#print(__doc__)

#***************************************************
# This is needed for installation through pip
#***************************************************
def TMonitorLite():
    main()
#***************************************************

import os.path, time
import board, busio
import adafruit_sgp30
import adafruit_mcp9808
import adafruit_bme280
import pandas as pd
from libTMonitor import *

#************************************
# Main - Scheduler
#************************************
def main():
    runAcq()
    
#************************************
# Run Acquistion
#************************************
def runAcq():
    config = Configuration()
 
    file = str(os.path.splitext(config.CSVfile)[0]+ "-Lite_" +\
                    str(datetime.now().strftime('%Y%m%d-%H%M%S'))+".csv")
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
 
    if config.TPsensor == 'BME280':
        TSens = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    elif config.TPsensor == 'MCP9808':
        TSens = adafruit_mcp9808.MCP9808(i2c)
        TSens.pressure = 0
        TSens.relative_humidity = 0
        # To initialise using a specified address:
        # Necessary when, for example, connecting A0 to VDD to make address=0x19
        # TSens = adafruit_mcp9808.MCP9808(i2c_bus, address=0x19)
 
    elapsed_sec = 0
 
    while True:
        temperature = TSens.temperature
        pressure = TSens.pressure
        humidity = TSens.relative_humidity
        pws = Pws(temperature,humidity)
        absHum = absHumidity(TSens.temperature,TSens.relative_humidity,pws)
        dewpoint = dewPointRH(temperature, humidity, pws)
            
        date = time.strftime("%Y%m%d")
        time1 = time.strftime("%H:%M:%S")
        
        if config.verbose:
            print("\n Lab: ", config.lab)
            print(" Name: ", config.name)
            print(" Measurement type: ", config.measType)
            print(" IP: ", ip)
            print(" TP sensor: ", config.TPsensor)
        
        print("T= %0.1f C | RH= %0.1f | date:%s | time: %s" % (temperature, humidity, str(date), str(time1)))
        time.sleep(1)
        elapsed_sec += 1
    
        sensData = {
            'lab' : config.lab,
            'date' : date,
            'time' : time1,
            'temperature' : temperature,
            'pressure' : pressure,
            'humidity' : humidity,
            'dewpoint' : dewpoint,
            }
            
        df = pd.DataFrame(sensData, index=[0])
    
        if config.saveCSV:
            try:
                if not os.path.exists(file):
                    df.to_csv(file, mode="a", header=True)
                else:
                    df.to_csv(file, mode="a", header=False)
            except:
                print("\n Saving to CSV failed!")
                
            
#************************************
# Main initialization routine
#************************************
if __name__ == "__main__":
    sys.exit(main())
