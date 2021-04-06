#!/usr/bin/env python3

'''
**********************************************************
*
* EnvMonitor - Environmental Tracking
* version: 20210405a
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

import os.path, time
import board, busio
import adafruit_sgp30
import adafruit_mcp9808
import adafruit_bme280
import pandas as pd
from libEnvMonitor import *

#************************************
''' Main - Scheduler '''
#************************************
def main():
    runAcq()
    
#************************************
''' Run Acquistion '''
#************************************
def runAcq():
    config = Configuration()
 
    file = str(os.path.splitext(config.CSVfile)[0]+ "-Lite_" +\
                    str(datetime.now().strftime('%Y%m%d-%H%M%S'))+".csv")
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
 
    # Create library object on our I2C port
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    # To initialise using the default address:
    #mcp = adafruit_mcp9808.MCP9808(i2c)
    mcp = adafruit_bme280.Adafruit_BME280_I2C(i2c)

    # To initialise using a specified address:
    # Necessary when, for example, connecting A0 to VDD to make address=0x19
    # mcp = adafruit_mcp9808.MCP9808(i2c_bus, address=0x19)
 
    print("SGP30 serial #", [hex(i) for i in sgp30.serial])
    sgp30.iaq_init()
    sgp30.set_iaq_baseline(config.eCO2_baseline, config.TVOC_baseline)
    elapsed_sec = 0
 
    while True:
        date = time.strftime("%Y%m%d")
        time1 = time.strftime("%H:%M:%S")
        
        #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
        print("eCO2 = %d ppm TVOC = %d ppb TempC = %0.1f date = %s time: %s" % (sgp30.eCO2, sgp30.TVOC, mcp.temperature, str(date), str(time))
        time.sleep(1)
        elapsed_sec += 1
    
        sensData = {
            'date' : date,
            'time' : time1,
            'temperature' : mcp.temperature,
            'pressure' : mcp.pressure,
            'humidity' : mcp.relative_humidity,
            'CO2' : sgp30.eCO2,
            'TVOC' : sgp30.TVOC,
            'eCO2_baseline' : hex(sgp30.baseline_eCO2),
            'TVOC_baseline' : hex(sgp30.baseline_TVOC),
            }
        df = pd.DataFrame(sensData, index=[0])
    
        if not os.path.exists(file):
            df.to_csv(file, mode="a", header=True)
        else:
            df.to_csv(file, mode="a", header=False)

        if elapsed_sec > 20:
            elapsed_sec = 0
            eCO2_baseline = sgp30.baseline_eCO2
            TVOC_baseline = sgp30.baseline_TVOC
            print(
                "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
                % (eCO2_baseline,TVOC_baseline))
            sgp30.set_iaq_baseline(eCO2_baseline,TVOC_baseline)
            
#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
