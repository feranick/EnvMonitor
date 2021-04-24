#!/usr/bin/env python3
  
import time
import board
import busio
import adafruit_sgp30
import adafruit_mcp9808
 
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
 
# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
# To initialise using the default address:
mcp = adafruit_mcp9808.MCP9808(i2c)

# To initialise using a specified address:
# Necessary when, for example, connecting A0 to VDD to make address=0x19
# mcp = adafruit_mcp9808.MCP9808(i2c_bus, address=0x19)
 
 
print("SGP30 serial #", [hex(i) for i in sgp30.serial])
sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)
elapsed_sec = 0
elapsed_2 = 0
 
while True:
    #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    print("eCO2 = %d ppm \t TVOC = %d ppb \t TempC = %0.1f" % (sgp30.eCO2, sgp30.TVOC, mcp.temperature))
    time.sleep(1)
    elapsed_sec += 1
    elapsed_2 += 1
    if elapsed_sec > 10:
        elapsed_sec = 0
        print(
            "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
            % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        )
    if elapsed_2 > 20:
        elapsed_2 = 0
        print(
            "**** SET Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
            % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        )
        sgp30.set_iaq_baseline(sgp30.baseline_eCO2, sgp30.baseline_TVOC)


