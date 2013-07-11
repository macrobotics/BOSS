#!/bin/sh

# Update Dependencies
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential
sudo apt-get install python python-imaging python-opencv python-numpy python-serial
sudo apt-get install git-core
sudo apt-get install arduino
sudo apt-get install minicom

# Configure Git
git config --global user.name "Trevor Stanhope"
git config --global user.email "tpstanhope@gmail.com"

# Configure Network
sudo mv /etc/network/interfaces /etc/network/interfaces.backup
sudo cp config/interfaces /etc/network/
sudo mv /etc/hosts /etc/hosts.backup
sudo cp config/hosts /etc

# Configure Configure
cp config/avrdude /usr/bin/avrdude
cp config/avrdude /usr/share/arduino/hardware/tools
cp config/avrdude.conf  /usr/share/arduino/hardware/tools
cp config/boards.txt  /usr/share/arduino/hardware/arduino
cp config/cmdline.txt /boot
cp config/inittab /etc
cp config/80-alamode.rules /etc/udev/rules.d
chown root /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
chgrp root /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
chmod a+s /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude

