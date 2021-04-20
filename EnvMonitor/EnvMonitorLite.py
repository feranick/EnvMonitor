#!/usr/bin/env python3
'''
**********************************************************
* EnvMonitor - Environmental Tracking
* version: 20210420a
* By: Nicola Ferralis <feranick@hotmail.com>
***********************************************************
'''
#print(__doc__)

#***************************************************
# This is needed for installation through pip
#***************************************************
def EnvMonitorLite():
    main()
#***************************************************

import os.path, time
import board, busio
import adafruit_sgp30
import adafruit_mcp9808
import adafruit_bme280
import adafruit_scd30
import pandas as pd
from libEnvMonitor import *

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
    
    print("Tsensor:",config.TPsensor)
    print("Gassensor:",config.Gassensor)
 
    if config.TPsensor == 'BME280':
        TSens = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        
    elif config.TPsensor == 'MCP9808':
        TSens = adafruit_mcp9808.MCP9808(i2c)
        TSens.pressure = 0
        TSens.relative_humidity = 0
        # To initialise using a specified address:
        # Necessary when, for example, connecting A0 to VDD to make address=0x19
        # TSens = adafruit_mcp9808.MCP9808(i2c_bus, address=0x19)
        
    elif config.TPsensor == 'SCD30':
        TSens = adafruit_scd30.Adafruit_SGP30(self.i2c)
        
    if config.Gassensor == 'SGP30':
        # Create library object on our I2C port
        GSens = adafruit_sgp30.Adafruit_SGP30(i2c)
        print("SGP30 serial #", [hex(i) for i in GSens.serial])
        GSens.iaq_init()
        GSens.set_iaq_baseline(config.eCO2_baseline, config.TVOC_baseline)
    elif config.Gassensor == 'SCD30':
        pass
    else:
        print("Gas Sensor not found. Exiting")
        return
 
    elapsed_sec = 0
 
    while True:
        if config.TPsensor == 'SCD30':
            data = TSens.data_available
        else:
            data = True
            
        if data:
            temperature = TSens.temperature
            if config.TPsensor == 'SCD30':
                pressure = TSens.ambient_pressure
            else:
                pressure = TSens.pressure
            humidity = TSens.relative_humidity
            pws = Pws(temperature,humidity)
            absHum = absHumidity(TSens.temperature,TSens.relative_humidity,pws)
            dewpoint = dewPointRH(temperature, humidity, pws)
        
            if config.Gassensor == 'SGP30':
                GSens.set_iaq_humidity(absHum)
                CO2 = GSens.eCO2
                TVOC = GSens.TVOC
                eCO2_baseline = hex(GSens.baseline_eCO2)
                TVOC_baseline = hex(GSens.baseline_TVOC)
                
            elif config.Gassensor == 'SGP30':
                CO2 = TSens.CO2
                TVOC = 0
                eCO2_baseline = 0
                TVOC_baseline = 0
                
            date = time.strftime("%Y%m%d")
            time1 = time.strftime("%H:%M:%S")
        
            #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
            print("eCO2= %d ppm | TVOC= %d ppb | T= %0.1f C | RH= %0.1f | date:%s | time: %s" % (CO2, TVOC, temperature, humidity, str(date), str(time1)))
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
                'CO2' : CO2,
                'TVOC' : TVOC,
                'eCO2_baseline' : eCO2_baseline,
                'TVOC_baseline' : TVOC_baseline,
                }
            df = pd.DataFrame(sensData, index=[0])
    
            if not os.path.exists(file):
                df.to_csv(file, mode="a", header=True)
            else:
                df.to_csv(file, mode="a", header=False)

            if elapsed_sec > 20:
                elapsed_sec = 0
                eCO2_baseline = GSens.baseline_eCO2
                TVOC_baseline = GSens.baseline_TVOC
                print(
                    "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
                    % (eCO2_baseline,TVOC_baseline))
                if config.resetBaseline:
                    GSens.set_iaq_baseline(eCO2_baseline,TVOC_baseline)
            
#************************************
# Main initialization routine
#************************************
if __name__ == "__main__":
    sys.exit(main())
