# Bale Ordinal Sorting System (BOSS) README.md
## Overview
BOSS is the server-client network behind the auto-bale collection
#system developed by McGill's ASABE Robotics Team. The primary
#objective of the system is to identify, locate, collect and sort "bales"
in a given area using a network of several workerbees (Slaves) and a
#central queen (Master). Each Slave consists of Raspberry Pi
#Microcomputer operating Debian "Wheezy" interfaced with an Arduino
#MEGA. The Master is conversely any computer, such as a laptop,
#acting as an ad-hoc server for the network. Using sensors, each Slave 
will acquire data on the locations of Bales on the field, which will
#then be relayed back to the Master.

## Installation
For installation instructions, please read INSTALL.md.
## Messages
Messages will be passed in tuples in the following format:
	
	MESSAGE = (HEADER,PAYLOAD)
	
### READY
READY message transmitted from Slaves to the Master when they come
online.
### START
START message transmitted from Master to Slaves starting the sort
process.
### STOP
STOP message transmitted from Master to Slaves stopping the sort
process.
### STATUS
STATUS message transmitted from Slaves to Master confering progress of
sort, i.e. number of bales collected and position
### FINISHED
FINISHED messaged transmitted rom Slaves to Master when task is
complete, i.e. all bales have been successfully stacked.

## Network Components
### Master
The Master will consist of a laptop which will host an ad-hoc wireless
#network. It's primary job is to display the productivity of the
#system and act as a DHCP server for the slaves on its network.

	IP=10.42.0.1
	HOSTNAME=master

### Slaves
The Slaves will consist of Raspberry Pi micro-computers which will
#connect automatically on boot to the Master's
#ad-hoc network. Each will be interfaced with an Arduino PLC
(Programmable Logic Controller) which will perform the physical
tasks for the Slave and relay back information to the Master. Because
of the limitations of IPv4, no more than 254 slaves can be
controlled by a single master, therefore larger operations would
require deparmentalization of working units.

	IP=10.42.0.2-255
	HOSTNAME=slaveN # where N is a number from 0 to 254
	
### Controllers
The Controller used on each Slave will be an Arduino Mega 2560,
although this can be substituted for any other PLC. The Controllers'
will act as the workhorse of the system, such as activating all
servos and acquiring sensor data.

## Hardware
### RaspberryPi Rev2
### Arduino MEGA 2560ADK
### Edimax EW-7811un

## Contributers
Trevor Stanhope


