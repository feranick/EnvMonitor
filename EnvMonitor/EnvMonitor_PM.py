#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170726a
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, math, json, os.path, time

global MongoDBhost

pms_gpio = 26

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
    conc_imp, conc = pms.collect()
    pms.printUI()
    sensData.extend([conc])
    pms.cleanup()
    
    #************************************
    ''' Make JSON and push to MongoDB '''
    #************************************
    conn = GEmongoDB(sensData,mongoFile)
    print("\n JSON:\n",conn.makeJSON(),"\n")
    print(" Pushing to MongoDB:")
    conn.pushToMongoDB()

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
        """
        Instantiate with the Pi and gpio to which the sensor
        is connected.
        """
        try:
            import RPi.GPIO
        except:
            self.GPIO = None
        else:
            self.GPIO = RPi.GPIO
        
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(self.GPIO.BOARD)
        self.GPIO.setup(gpio,self.GPIO.IN)

        self.gpio = gpio
        self.collectionTime = 30

    def collect(self):
        runTime = time.time()
        lowpulseoccupancy = 0
        self.GPIO.remove_event_detect(self.gpio)
        self.GPIO.add_event_detect(self.gpio, self.GPIO.BOTH, bouncetime = 1)
        
        while time.time() - runTime < self.collectionTime:
            print(" Waiting",int(time.time() - runTime),
                  "/",int(self.collectionTime),"s for PM sensor...", end="\r")
            #time.sleep(0.005)
            startTime = time.time()
            if self.GPIO.event_detected(self.gpio):
                self.GPIO.remove_event_detect(self.gpio)
                duration = time.time() - startTime
                lowpulseoccupancy = lowpulseoccupancy+duration
                self.GPIO.add_event_detect(self.gpio, self.GPIO.BOTH, bouncetime=1)
    
        self.ratio = lowpulseoccupancy*100/(self.collectionTime);
        self.conc_imp = 1.1*pow(self.ratio,3)-3.8*pow(self.ratio,2)+520*self.ratio+0.62
        self.conc = self.conc_imp*0.000238 # concentration in particles/L
        return (self.conc_imp, self.conc)

    def printUI(self):
        print(" Particulate PM2.5: \n particles/m^3: {0:0.4f}".format(self.conc),
              "\n particles/cu-ft: {0:0.2f}".format(self.conc_imp))

    def cleanup(self):
        self.GPIO.cleanup()

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
            'PM2.5_particles_m3' : '{0:0.3f}'.format(self.data[7]),
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
