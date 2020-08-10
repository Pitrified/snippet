#!/bin/bash

# magic to use this in a cron job
# https://askubuntu.com/a/743024
# PID=$(pgrep gnome-session)
# export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)

BASE_PYR="/home/pietro/Pictures/Wallpapers/pyramids/pyr_"
HOUR=$(date +"%H")
EXT=".png"
echo $HOUR
IMG=$BASE_PYR$HOUR$EXT
echo $IMG
