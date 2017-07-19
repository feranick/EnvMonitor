#!/bin/bash

#####################################
#
# EnvMonitor IP and lanucher
#
# v. 20170719a
#
# Nicola Ferralis <ferralis@mit.edu>
#
#####################################

lab="Lab1"

remote="pi@server.com:/home/pi/EnvMonitor-logs"
file="/home/pi/EnvMonitor/EnvMonitor_$lab.txt"

sleep 60
IP=$(hostname -I)

echo "EnvMonitor lab: "$lab > $file
echo "IP: "$IP >> $file
echo $(date) >> $file
scp $file $remote

# Eventually, the actual Softare for running the Environmental monitoring could be launched from here
