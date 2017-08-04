#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170803a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, math, json, os.path, time
from Adafruit_BME280 import *

global MongoDBhost

pms_gpio = 15  # (GPIO15, pin 10)

def main():
    if len(sys.argv)<3 or os.path.isfile(sys.argv[2]) == False:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongoFile>\n')
        return
    
    lab = sys.argv[1]
    mongoFile = sys.argv[2]
    
    #************************************
    ''' Read from T/RH sensor '''
    #************************************
    trhSensor = TRHSensor(lab)
    sensData = trhSensor.readSensors()
    trhSensor.printUI()
    
    #************************************
    ''' Read from PM sensor '''
    #************************************
    pms = PMSensor(pms_gpio)
    conc, conc_pcf, conc_ugm3, conc_aqi = pms.collect()
    pms.printUI()
    sensData.extend([conc, conc_aqi])
    pms.cleanup()
    
    #************************************
    ''' Make JSON and push to MongoDB '''
    #************************************
    conn = GEmongoDB(sensData,mongoFile)
    #print(" JSON:\n",conn.makeJSON(),"\n")
    print(" Pushing to MongoDB:")
    #conn.pushToMongoDB()

#************************************
''' Class T/RH Sensor '''
#************************************
class TRHSensor:
    def __init__(self, lab):
        self.lab = lab
        self.date = time.strftime("%Y%m%d")
        self.time = time.strftime("%H:%M:%S")
        self.sensData = []
        self.ip = getIP()

    #************************************
    ''' Read Sensors '''
    #************************************
    def readSensors(self):
        self.sensData.extend([self.lab, self.ip, self.date, self.time])
        try:
            sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
            self.sensData.extend([sensor.read_temperature(),
                                  sensor.read_pressure() / 100,
                                  sensor.read_humidity()])
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.sensData.extend([0.0,0.0,0.0])
        return self.sensData

    #************************************
    ''' Print Values on screen '''
    #************************************
    def printUI(self):
        print("\n Lab: ", self.lab)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.1f} deg C".format(self.sensData[4]))
        print(" Pressure = {0:0.1f} hPa".format(self.sensData[5]))
        print(" Humidity = {0:0.1f} %".format(self.sensData[6]),"\n")

#************************************
''' Class Particulate Sensor '''
#************************************
class PMSensor:
    '''
    A class to read a Shinyei PPD42NS Dust Sensor, e.g. as used
    in the Grove dust sensor.

    This code calculates the percentage of low pulse time and
    calibrated concentration in particles per 1/100th of a cubic
    foot at user chosen intervals.
    '''

    def __init__(self, gpio):
        try:
            import pigpio
        except:
            self.GPIO = None
        else:
            self.GPIO = pigpio
        
        self.collectionTime = 30
        self.pi = pigpio.pi()
        self.gpio = gpio
        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0
        self.ratio = 0
        
        self.pi.set_mode(gpio, pigpio.INPUT)
        self._cb = self.pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def collect(self):
        runTime = time.time()
        while time.time() - runTime <= self.collectionTime:
            print(" Waiting",int(time.time() - runTime),
                  "/",int(self.collectionTime),"s for PM sensor...", end="\r")
        self.read()
        return (self.conc, self.conc_pcf, self.conc_ugm3, self.conc_aqi)
    
    def read(self):
        interval = self._low_ticks + self._high_ticks
        if interval > 0:
            self.ratio = float(self._low_ticks)/float(interval)*100.0
        else:
            self.ratio = 0
        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0
        self.conc_pcf = 1.1*pow(self.ratio,3)-3.8*pow(self.ratio,2)+520*self.ratio+0.62
        self.conc = self.conc_pcf/0.2831685 # concentration in particles/L
        self.conc_ugm3 = self.pcf_to_ugm3(self.conc)
        self.conc_aqi = self.ugm3_to_aqi(self.conc_ugm3)
        
    def _cbf(self, gpio, level, tick):
        if self._start_tick is not None:
            ticks = self.GPIO.tickDiff(self._last_tick, tick)
            self._last_tick = tick
            if level == 0: # Falling edge.
                self._high_ticks = self._high_ticks + ticks
            elif level == 1: # Rising edge.
                self._low_ticks = self._low_ticks + ticks
            else: # timeout level, not used
                pass
        else:
            self._start_tick = tick
            self._last_tick = tick

    def pcf_to_ugm3(self, conc_pcf):
        '''
        Convert concentration of PM2.5 particles per 0.01 cubic feet to µg/ metre cubed
        this method outlined by Drexel University students (2009) and is an approximation
        does not contain correction factors for humidity and rain
        '''
        # Assume all particles are spherical, with a density of 1.65E12 µg/m3
        densitypm25 = 1.65 * math.pow(10, 12)
        
        # Assume the radius of a particle in the PM2.5 channel is .44 µm
        rpm25 = 0.44 * math.pow(10, -6)
        
        # Volume of a sphere = 4/3 * pi * radius^3
        volpm25 = (4/3) * math.pi * (rpm25**3)
        
        # mass = density * volume
        masspm25 = densitypm25 * volpm25
        
        # parts/m3 =  parts/foot3 * 3531.5
        # µg/m3 = parts/m3 * mass in µg
        conc_ugm3 = conc_pcf * 3531.5 * masspm25
        return conc_ugm3
    
    def ugm3_to_aqi(self, ugm3):
        '''
        Convert concentration of PM2.5 particles in µg/ metre cubed to the USA 
        Environment Agency Air Quality Index - AQI
        https://en.wikipedia.org/wiki/Air_quality_index
	    Computing_the_AQI
        https://goo.gl/biYDqq
        '''
        cbreakpointspm25 = [ [0.0, 12, 0, 50],\
                        [12.1, 35.4, 51, 100],\
                        [35.5, 55.4, 101, 150],\
                        [55.5, 150.4, 151, 200],\
                        [150.5, 250.4, 201, 300],\
                        [250.5, 350.4, 301, 400],\
                        [350.5, 500.4, 401, 500], ]
        C=ugm3
        if C > 500.4:
            aqi=500
        else:
           for breakpoint in cbreakpointspm25:
               if breakpoint[0] <= C <= breakpoint[1]:
                   Clow = breakpoint[0]
                   Chigh = breakpoint[1]
                   Ilow = breakpoint[2]
                   Ihigh = breakpoint[3]
                   aqi=(((Ihigh-Ilow)/(Chigh-Clow))*(C-Clow))+Ilow
        return aqi

    def printUI(self):
        print("\n Particulate Sensor for PM2.5:     \n  particles/L: {0:0.4f}".format(self.conc),
              "\n  particles/cu-ft: {0:0.2f}".format(self.conc_pcf),
              "\n  ug/m^3: {0:0.5f}".format(self.conc_ugm3),
              "\n  aqi: ",self.conc_aqi, "\n")

    def cleanup(self):
        self.pi.stop()

#************************************
''' Class Database '''
#************************************
class GEmongoDB:
    def __init__(self, data, file):
        self.data = data
        with open(file, 'r') as f:
            f.readline()
            self.hostname = f.readline().rstrip('\n')
            f.readline()
            self.port_num = f.readline().rstrip('\n')
            f.readline()
            self.dbname = f.readline().rstrip('\n')
            f.readline()
            self.username = f.readline().rstrip('\n')
            f.readline()
            self.password = f.readline().rstrip('\n')

    def connectDB(self):
        from pymongo import MongoClient
        client = MongoClient(self.hostname, int(self.port_num))
        auth_status = client[self.dbname].authenticate(self.username, self.password, mechanism='SCRAM-SHA-1')
        print(' Authentication status = {0} \n'.format(auth_status))
        return client

    def printAuthInfo(self):
        print(self.hostname)
        print(self.port_num)
        print(self.dbname)
        print(self.username)
        print(self.password)

    def makeJSON(self):
        dataj = {
            'lab' : self.data[0],
            'IP' : self.data[1],
            'date' : self.data[2],
            'time' : self.data[3],
            'temperature' : '{0:0.1f}'.format(self.data[4]),
            'pressure' : '{0:0.1f}'.format(self.data[5]),
            'humidity' : '{0:0.1f}'.format(self.data[6]),
            'PM2.5_particles_L' : '{0:0.3f}'.format(self.data[7]),
            'aqi' : self.data[7],
            }
        return json.dumps(dataj)

    def pushToMongoDB(self):
        jsonData = self.makeJSON()
        client = self.connectDB()
        db = client.Tata
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(jsonData))
            print(" Data entry successful (id:",db_entry.inserted_id,")\n")
        except:
            print(" Data entry failed.\n")

#************************************
''' Get system IP '''
#************************************
def getIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
