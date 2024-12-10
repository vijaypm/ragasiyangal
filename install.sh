#!/bin/sh
if [ ! "`whoami`" = "root" ]
then
    echo "\nPlease run script as root."
    exit 1
fi
mkdir -p /opt/ragasiyangal
cp ragasiyangal /opt/ragasiyangal/
cp ragasiyangal.desktop ~/.local/share/applications/
cp ragasiyangal.png /opt/ragasiyangal/
apt-get install --reinstall libxcb-xinerama0
apt-get install libxcb-cursor-dev
