# GREEN.py
# License: Creative Commons 2013, Trevor Stanhope

# Setup
from numpy import * # image processing
import numpy
from PIL import Image # image processing
from cv2 import * # image capture
from time import *
import time
import serial
from serial import SerialException
import socket
import sys
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
HOST = 'localhost'
PORT = 10000
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 5
arduino = serial.Serial(DEVICE, BAUD)
camera = VideoCapture(CAMERA_INDEX)
camera.set(3,WIDTH)
camera.set(4,HEIGHT)

# Gather
gathered = 0
while (gathered < 4):
  print('---------------------')
  
  ## Determine location
  (success, frame) = camera.read() # capture image as array
  if success:
    ### Parse Image
    raw = Image.fromarray(frame)
    BGR = raw.split()
    B = array(BGR[0].getdata(), dtype=float32)
    G = array(BGR[1].getdata(), dtype=float32)
    R = array(BGR[2].getdata(), dtype=float32)
    try:
      NDI = (BIAS*G)/(R+B) # convert to normalized difference index
    except ValueError:
      NDI = ((BIAS+1)*G)/(R+B+1) # convert to normalized difference index
    RNDI = NDI.reshape(HEIGHT,WIDTH) # rows by columns
    columns = RNDI.sum(axis=0)
    
    ### Find Objects
    colored = numpy.mean(columns) + numpy.std(columns)
    x = 0
    objects = []
    sizes = []
    offsets = []
    while (x < WIDTH-1):
      if (columns[x] > colored):
        start = x
        while (columns[x] > colored) and (x < WIDTH-1):
          x += 1
        end = x
        sizes.append((end - start))
        offsets.append(start + (end - start)/2)
      else:
        x += 1
        
    ### Determine Action
    closest = sizes.index(numpy.max(sizes))
    distance = WIDTH - numpy.max(sizes)
    direction = offsets[closest]
    print('Distance: ' + str(distance))
    print('Direction: ' + str(direction))
    if (direction < (CENTER - THRESHOLD)):
      print('Left')
      COMMAND = 'l'
    elif (direction > (CENTER + THRESHOLD)):
      print('Right')
      COMMAND = 'r'
    elif (distance > RANGE):
      print('Forward')
      COMMAND = 'f'
    else:
      print('Grab')
      COMMAND = 'g'
    
  ## Send command
  try:
    arduino.write(COMMAND)
    RESPONSE = arduino.readline()
    print(RESPONSE)  
    #### EXPAND ####
    if (COMMAND == 'g') and (RESPONSE == 1):
      gathered += 1
  except ValueError:
    print("ValueError: Failed to parse signal, retrying...")
  except OSError:
    print("OSError: Connection lost, retrying...")
  except SerialException:
    print("Serial Exception: Connection lost, retrying...")
  except SyntaxError:
    print("Syntax Error: Failed to parse signal, retrying...")
  except KeyError:
    print("KeyError: Failed to parse signal, retrying...")
    
"""
# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(data + "\n", (HOST, PORT))
received = sock.recv(1024)
"""
