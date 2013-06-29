## Imports
from socket import *
import json
import serial, time, ast
from serial import SerialException
from time import gmtime, strftime
import RPi.GPIO as GPIO # PWM pins
import numpy # image processing
from PIL import Image # image processing
from cv2 import * # image capture
from itertools import cycle # circular lists
from time import *

## Constants
BAUD = 9600
DEV = '/dev/ttyACM0'
INTERVAL = 1
HOST_IN = 'localhost'
HOST_OUT = ''
PORT_IN = 30000
PORT_OUT = 30001
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 5
CAMERA_INDEX = 0
WIDTH = 160
HEIGHT = 120

## Bind Arduino
arduino = serial.Serial(DEV, BAUD)

## Bind Socket
address_in = (HOST_IN,PORT_IN)
address_out = (HOST_OUT,PORT_OUT)
socket_out = socket(AF_INET, SOCK_STREAM) # create a new socket object (serv)
socket_out.bind((address_out)) # bind socket to address with new tuple
socket_out.listen(MAX_CONNECTIONS) # maximum number of queued connections

## Bind Camera
camera = VideoCapture(CAMERA_INDEX)
camera.set(3,WIDTH)
camera.set(4,HEIGHT)

## Loop
while (stacked < 4):
	# Receive Command
    socket_in = socket(AF_INET, SOCK_STREAM) # tmp socket
    socket_in.connect((address_in))
    command_raw = socket_in.recv(BUFFER_SIZE) # get message as string
    command_parsed = json.loads(command_raw) # re-encode message as json
    command_type = command_parsed["type"] # parse header
    command_data = command_parsed["data"] # parse payload
    socket_in.close()
    
    # Execute Actions
    if (command_type == 1):
        (response_type, response_data) = (1,None)
    else if (command_type == 2):
        (response_type, response_data) = (2,None)
    else if (command_type == 3):
        (response_type, response_data) = (3,None)
    else if (command_type == 4):
        (response_type, response_data) = (4,None)
    else if (command_type == 5):
        (response_type, response_data) = (5,None)
    else:
        (response_type, response_data) = (0,None)
    
    # Send Response
    (connection,address) = socket_out.accept() # accept the connection
    response = json.dumps({'type':response_type, 'data':response_data}) # dump to string
    conn.send(response)
    conn.close()
