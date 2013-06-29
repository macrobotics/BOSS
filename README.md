# Bale Ordinal Sorting System (BOSS)
## Master (Laptop)
### Python and GTK
The display for the Master is rendered using python and gtk2. First it
is important to update Apt:

	sudo apt-get update && sudo apt-get upgrade
	
Then install python and the GTK libraries:

	sudo apt-get install python python-simplejson python-gtk2
	
## Slaves (RaspberryPi)
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

### Software
Update Apt:
  
  sudo apt-get update && sudo apt-get upgrade
  
Install python and the additional modules:

  sudo apt-get install python python-opencv python-imaging python-numpy
  
Install Arduino:

  sudo apt-get install arduino
