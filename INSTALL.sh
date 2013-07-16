#!/bin/sh

# Update Dependencies
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential -y
sudo apt-get install python python-imaging python-opencv python-numpy python-serial -y
sudo apt-get install git-core -y
sudo apt-get install arduino arduino-mk -y
sudo apt-get install minicom -y

# Configure Git
git config --global user.name "Trevor Stanhope"
git config --global user.email "tpstanhope@gmail.com"

# Configure Network
sudo mv /etc/network/interfaces /etc/network/interfaces.backup
sudo cp config/interfaces /etc/network/
sudo mv /etc/hosts /etc/hosts.backup
sudo cp config/hosts /etc

# Configure Controller
sudo cp config/avrdude /usr/bin/avrdude
sudo cp config/avrdude /usr/share/arduino/hardware/tools
sudo cp config/avrdude.conf  /usr/share/arduino/hardware/tools
sudo cp config/boards.txt  /usr/share/arduino/hardware/arduino
sudo cp config/cmdline.txt /boot
sudo cp config/inittab /etc
sudo cp config/80-alamode.rules /etc/udev/rules.d
sudo chown root /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
sudo chgrp root /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
sudo chmod a+s /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
sudo mv libraries/AFMotor /usr/share/arduino/libraries

# Configure Start-on-Boot
sudo mv /etc/rc.local /etc/rc.local.backup
sudo cp config/rc.local /etc/
sudo mv code/Worker/Worker.py /usr/bin/
sudo chmod +x /usr/bin/Worker.py
