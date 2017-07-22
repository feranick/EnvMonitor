#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170719b
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, time, json, os.path
#from Adafruit_BME280 import *

global MongoDBhost

def main():
    if len(sys.argv)<3 or os.path.isfile(sys.argv[2]) == False:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongoFile>\n')
        return
    
    mongoFile = sys.argv[2]

    lab = sys.argv[1]
    sensor1 = TRHSensor(lab)
    sensor1.readSensors()
    sensor1.printUI()
        
    print(" JSON:\n",sensor1.makeJSON(),"\n")
    
    print(" Pushing to MongoDB:")
    sensor1.pushToMongoDB(mongoFile)

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
        try:
            sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
            self.sensData.append(sensor.read_temperature())
            self.sensData.append(sensor.read_pressure() / 100)
            self.sensData.append(sensor.read_humidity())
        except:
            print("\n SENSOR NOT CONNECTED ")
            self.sensData.append(0.0)
            self.sensData.append(0.0/100)
            self.sensData.append(0.0)
        return self.sensData

    #************************************
    ''' Print Values on screen '''
    #************************************
    def printUI(self):
        print("\n Lab: ", self.lab)
        print(" IP: ", self.ip)
        print(" Date: ", self.date)
        print(" Time: ", self.time)
        print(" Temperature = {0:0.3f} deg C".format(self.sensData[0]))
        print(" Pressure = {0:0.2f} hPa".format(self.sensData[1]))
        print(" Humidity = {0:0.2f} %".format(self.sensData[2]),"\n")

    #************************************
    ''' Make JSON '''
    #************************************
    def makeJSON(self):
        data = {
            'lab' : self.lab,
            'IP' : self.ip,
            'date' : self.date,
            'time' : self.time,
            'temperature' : self.sensData[0],
            'pressure' : self.sensData[1],
            'humidity' : self.sensData[2]
        }
        return json.dumps(data)
        
    #****************************************
    ''' Push to Mongo '''
    #****************************************
    def pushToMongoDB(self, file):
        connDB1 = GEmongoDB(file)
        #connDB1.printAuthInfo()
        client = connDB1.connectDB()
        db = client.Tata
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(self.makeJSON()))
            print(" Data entry successful (id:",db_entry.inserted_id,")\n")
        except:
            print(" Data entry failed.\n")

#************************************
''' Class Particulate Sensor '''
#************************************
class PMSensor:
    
    import math
    import RPi.GPIO as GPIO

    """
    A class to read a Shinyei PPD42NS Dust Sensor, e.g. as used
    in the Grove dust sensor.

    This code calculates the percentage of low pulse time and
    calibrated concentration in particles per 1/100th of a cubic
    foot at user chosen intervals.

    You need to use a voltage divider to cut the sensor output
    voltage to a Pi safe 3.3V (alternatively use an in-line
    20k resistor to limit the current at your own risk).
    """

    def __init__(self, gpio):
        """
        Instantiate with the Pi and gpio to which the sensor
        is connected.
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        self.gpio = gpio
        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0

        GPIO.setup(gpio,GPIO.OUT)
        #pi.set_mode(gpio, pigpio.INPUT)
        
        self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def read(self):
        """
        Calculates the percentage low pulse time and calibrated
        concentration in particles per 1/100th of a cubic foot
        since the last read.

        For proper calibration readings should be made over
        30 second intervals.

        Returns a tuple of gpio, percentage, and concentration.
        """
        interval = self._low_ticks + self._high_ticks

        if interval > 0:
            ratio = float(self._low_ticks)/float(interval)*100.0
            conc = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62;
        else:
            ratio = 0
            conc = 0.0

        self._start_tick = None
        self._last_tick = None
        self._low_ticks = 0
        self._high_ticks = 0

        return (self.gpio, ratio, conc)

    def _cbf(self, gpio, tick):

        if self._start_tick is not None:

            ticks = self.tickDiff(self._last_tick, tick)
            self._last_tick = tick
            self._high_ticks = self._high_ticks + ticks
            
            '''
            if level == 0: # Falling edge.
                self._high_ticks = self._high_ticks + ticks

            elif level == 1: # Rising edge.
                self._low_ticks = self._low_ticks + ticks

            else: # timeout level, not used
                pass
            '''
       else:
            self._start_tick = tick
            self._last_tick = tick
         

    def pcs_to_ugm3(self, concentration_pcf):
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
        concentration_ugm3 = concentration_pcf * 3531.5 * masspm25
        
        return concentration_ugm3


    def tickDiff(t1, t2):
        '''
        Returns the microsecond difference between two ticks.
        t1:= the earlier tick
        t2:= the later tick
        '''
        tDiff = t2 - t1
        if tDiff < 0:
            tDiff += (1 << 32)
        return tDiff

#************************************
''' Class Database '''
#************************************
class GEmongoDB:
    def __init__(self, file):
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
