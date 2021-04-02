#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, math, json, os.path, time, configparser, logging, sched
from datetime import datetime
import numpy as np
import pandas as pd

#************************************
''' Main - Scheduler '''
#************************************
def main():

    sensData = {
            'lab' : 0,
            'measType' : 0,
            'TPsensor' : 'MCP9808',
            'Gassensor' : 'SGP30',
            'IP' : 2,
            'date' : 3,
            'time' : 4,
            'temperature' : 5,
            'pressure' : 6,
            'humidity' : 6,
            'dewpoint' : 6,
            'altitude' : 7,
            'sealevel' : 7,
            'CO2' : 8,
            'TVOC' : 9,
            }

    file = 'test.csv'
    df = pd.DataFrame(sensData, index=[0])
    if not os.path.exists(file):
        df.to_csv(file, mode="a", header=True)
    else:
        df.to_csv(file, mode="a", header=False)
    
    
    

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
