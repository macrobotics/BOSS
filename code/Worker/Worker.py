#!/usr/bin/python
# Worker.py

# Imports
from serial import SerialException
from socket import *
from numpy import *
from PIL import Image 
from cv2 import * # image capture
from time import *
import numpy
import time
import json
import serial
import sys

# Constants
ADDRESS_IN = ('localhost',30000)
ADDRESS_OUT = ('',30001)
BUFFER_SIZE = 4096
QUEUE_MAX = 5
BAUD = 9600
DEVICE = '/dev/ttyACM1'
CAMERA_INDEX = 1
WIDTH = 640
HEIGHT = 480
CENTER = WIDTH/2
THRESHOLD = CENTER/2
RANGE = CENTER
BIAS = WIDTH/2
INTERVAL = 1
MAX_CONNECTIONS = 5

# Bind Socket
SOCKET_OUT = socket(AF_INET,SOCK_STREAM) # create a new socket object (serv)
SOCKET_OUT.bind((ADDRESS_OUT)) # bind socket to address with new tuple
SOCKET_OUT.listen(QUEUE_MAX) # maximum number of queued connections

# Loop
while 1:
  try: 
    print('--------------')
    print('Listening for Server...')
    SOCKET_IN = socket(AF_INET,SOCK_STREAM) # tmp socket
    SOCKET_IN.connect((ADDRESS_IN))
    print('...Success.')
  
    print('Receiving COMMAND...')
    COMMAND = SOCKET_IN.recv(BUFFER_SIZE) # get message as string
    PARSED = json.loads(COMMAND) # re-encode message as json
    DATA = PARSED['DATA']
    SOCKET_IN.close()
    print('...Success.')
  
    print('Talking to Server...')
    CONNECTION,ADDRESS = SOCKET_OUT.accept() # accept the connection
    print('...Success.')
  
    print('Sending RESPONSE...')
    RESPONSE = json.dumps({'DATA':'SUCCESS'}) # dump to string
    CONNECTION.send(RESPONSE)
    CONNECTION.close()
    print("...Success.")

  except Exception:
    print('...Failure.')
    pass
