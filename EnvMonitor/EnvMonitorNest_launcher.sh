#!/bin/bash
#####################################
# EnvMonitorNest launcher
# v. 20210428a
# Nicola Ferralis <feranick@hotmail.com>
#####################################

echo "Enter user code:"
read code
nohup EnvMonitorNest $code  > ~/EnvMonLog.txt 2>&1 &
