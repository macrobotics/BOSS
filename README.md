# Bale Optical Stacking System (BOSS)
## Server (Laptop)
### Python and GTK
The display for the Master is rendered using python and gtk2. First it
is important to update Apt:

	  sudo apt-get update && sudo apt-get upgrade
	
Then install python and the GTK libraries:

	  sudo apt-get install python python-gtk2
	
## Workers (RaspberryPi)
### Hardware Configuration
1. Connect RPi to wired ethernet.
2. Download 2013-05-25-wheezy-raspbian.img.

    wget http://downloads.raspberrypi.org/images/raspbian/2013-05-25-wheezy-raspbian/2013-05-25-wheezy-raspbian.zip
  
3. Unzip the image:

    unzip 2013-05-25-wheezy-raspbian.zip
  
4. Unmount all partitions of the SD card:

    sudo umount /dev/mmcblk0p*
    
5. From the directory of the image file (this will take a while):

    dd bs=4M if=2013-05-25-wheezy-raspbian.img of=/dev/mmcblk0
    
6. The first time the device is booted, it will prompt to set configurations or run this command:

    raspi-config
    
7. When in the configuration editor, the following are ideal settings:
    
    Keyboard layout? --> English US
    Overclocking? --> High
    SSH? --> Enable
    Desktop on Boot? --> Disable
    Memory Split --> 256MB

### Install Worker's Software
To install a fresh system, simply execute INSTALL.sh from the BOSS/ directory:
  
    sh INSTALL.sh

### Updating Controller
1. Copy the newest version of Controller.ino and Makefile in /home/pi.

    scp Controller.ino Makefile pi@green:/home/pi

2. Change to the build directory (assuming files are in /home/pi) then clean it:

    cd /home/pi
    make clean

3. Compile the code:
    
    make

4. Upload the compiled code:

    make upload

### Updating Worker.py
1. Copy the newest version of Worker.py in /home/pi

    scp Worker.py pi@green:/home/pi
