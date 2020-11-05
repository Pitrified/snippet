#!/bin/bash

# magic to use this in a cron job
# https://askubuntu.com/a/743024
# info on cut https://stackoverflow.com/a/816824

PID=$(pgrep -a gnome-session | grep ubuntu | cut -d ' ' -f 1)
export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)

# randomize the choice
# https://askubuntu.com/a/510135
DIR="~/Pictures/sfondi/randfolder"
PIC=$(ls $DIR/* | shuf -n1)
gsettings set org.gnome.desktop.background picture-uri "file://$PIC"

# cron line
# */3 * * * * /bin/bash ~/Pictures/sfondi/rand_changer.sh
