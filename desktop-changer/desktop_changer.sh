#!/bin/bash

# magic to use this in a cron job
# https://askubuntu.com/a/743024
# info on cut https://stackoverflow.com/a/816824

PID=$(pgrep -a gnome-session | grep ubuntu | cut -d ' ' -f 1)
echo $PID
# for x in $PID
# do
#     echo pid $x
#     export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$x/environ|cut -d= -f2-)
# done
# export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)
export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)

BASE_PYR="$HOME/snippet/desktop-changer/out_pyramids/pyr_"
HOUR=$(date +"%H")
# echo $HOUR
EXT=".jpg"
IMG=$BASE_PYR$HOUR$EXT
echo $IMG
gsettings set org.gnome.desktop.background picture-uri "file://$IMG"
