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
import socket
import time
import json
import serial
import sys
import ast

# Setup
ADDRESS_IN = ('localhost',50000)
ADDRESS_OUT = ('localhost',50001)
BUFFER_SIZE = 4096
QUEUE_MAX = 5
BAUD = 9600
DEVICE = '/dev/ttyACM0'
CAMERA_INDEX = 1
WIDTH = 640
HEIGHT = 480
CENTER = WIDTH/2
THRESHOLD = CENTER/2
RANGE = CENTER
BIAS = 2
MINIMUM = 0.01
INTERVAL = 1
MAX_CONNECTIONS = 5

# Class Worker
class BOSS_Worker:
  def __init__(self):
    try:
      print('Setting up Camera...')
      self.camera = VideoCapture(CAMERA_INDEX)
      self.camera.set(3,WIDTH)
      self.camera.set(4,HEIGHT)
      print('...Success.')
    except Exception:
      print('...Failure.')
    
    try:
      print('Setting up Arduino...')
      self.arduino = serial.Serial(DEVICE, BAUD)
      print('...Success.')
    except Exception:
      print('...Failure.')
      
    try:
      print('Initializing Worker...')
      self.connected_out = False
      self.connected_in = False
      print('...Success.')
    except Exception:
      print('...Failure.')

  def use_camera(self):
    (success, frame) = self.camera.read()
    raw = Image.fromarray(frame)
    BGR = raw.split()
    B = array(BGR[0].getdata(), dtype=float32)
    G = array(BGR[1].getdata(), dtype=float32)
    R = array(BGR[2].getdata(), dtype=float32)
    NDI = ((BIAS)*G)/(R+B+MINIMUM)
    RNDI = NDI.reshape(HEIGHT,WIDTH) # rows by columns
    columns = RNDI.sum(axis=0)
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
    closest = sizes.index(numpy.max(sizes))
    distance = WIDTH - numpy.max(sizes)
    direction = offsets[closest]

  def connect(self):
    while (self.connected_out == False) or (self.connected_in == False):
      try:
        print('Establishing SEND Port to Server...')
        self.socket_out = socket.socket(AF_INET,SOCK_STREAM)
        self.socket_out.bind((ADDRESS_OUT))
        self.socket_out.listen(QUEUE_MAX)
        (self.connection,self.address) = self.socket_out.accept()
        self.connected_out = True
        print('...Success.')
      except socket.error as SocketError:
        print('...Failure')
        self.connected_out = False
        self.socket_out.close()
        pass

      try:
        print('Establishing RECEIVE Port from Server...')
        self.socket_in = socket.socket(AF_INET,SOCK_STREAM) # tmp socket
        self.socket_in.connect((ADDRESS_IN))
        self.connected_in = True
        print('...Success.')
      except socket.error as error:
        self.socket_in.close()
        self.connected_in = False
        print('...Failure.')
        pass
      
  def disconnect(self):
    try:
      print('Disconnecting from Server...')
      self.socket_in.close()
      self.connection.close()
      print('...Success')
    except Exception:
      print('...Failure')
      pass

  def receive_command(self):
    try: 
      print('Receiving COMMAND...')
      command = self.socket_in.recv(BUFFER_SIZE)
      print(str(command))
      parsed_command = json.loads(command)
      action = parsed_command['ACTION']
      print('...Success.')
    except ValueError:
      print('...Failure.')
    except socket.error as SocketError:
      print('...Connection Failure.')

  def send_response(self, status):   
    try:
      print('Sending RESPONSE...')
      response = json.dumps({'STATUS':status})
      self.connection.send(response)
      print("...Success.")
    except Exception:
      print("...Failure.")

  def execute_action(self, command):
    if (command == 'START'):
      self.action = 'START'
    if (command == 'STOP'):
      self.action == 'STOP'
    if (command == 'DISCONNECT'):
      self.action == 'DISCONNECT'
      self.connected_in = False
      self.connected_out = False
      self.disconnect()
    else:
      self.action = 'UNKNOWN'
    
    self.arduino.write(self.action)
    self.arduino.readline()

if __name__ == "__main__":
  Worker = BOSS_Worker()
  while 1:
    Worker.connect()
    while (Worker.connected_in) or (Worker.connected_out):
      Worker.use_camera()
      command = Worker.receive_command()
      response = Worker.execute_action(command)
      Worker.send_response('COMPLETED')
    else:
      Worker.disconnect()
