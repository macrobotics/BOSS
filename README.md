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
Download 2013-05-25-wheezy-raspbian.img.

    wget http://downloads.raspberrypi.org/images/raspbian/2013-05-25-wheezy-raspbian/2013-05-25-wheezy-raspbian.zip
  
Unzip the image:

    unzip 2013-05-25-wheezy-raspbian.zip
  
Unmount all partitions of the SD card:

    sudo umount /dev/mmcblk0p*
    
From the directory of the image file (this will take a while):

    dd bs=4M if=2013-05-25-wheezy-raspbian.img of=/dev/mmcblk0
    
The first time the device is booted, it will prompt to set configurations.
This process can be repeated later with the command:

    raspi-config
    
When in the configuration editor, the following are ideal settings:

1. Keyboard layout? --> English US
2. Overclocking? --> High
3. SSH? --> Enable
4. Desktop on Boot? --> Disable
5. Memory Split --> 256MB

### Worker's 'Software
To install the system, simply execute INSTALL.sh from the BOSS/ directory:
  
    sh INSTALL.sh
