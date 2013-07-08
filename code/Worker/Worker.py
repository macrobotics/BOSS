#!/usr/bin/python
# Worker.py

# Imports
from serial import SerialException
from socket import *
from numpy import *
from PIL import Image 
from cv2 import VideoCapture
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
RANGE = WIDTH/1.5
BIAS = 2
MINIMUM = 0.01
INTERVAL = 1
MAX_CONNECTIONS = 5
TURN = pi/4
TRAVEL = 0.5

# Class Worker
class BOSS_Worker:
  ## Initialize Worker robot.
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
      self.command = None
      self.response = None
      self.action = None
      self.previous_actions = []
      self.green_objects = []
      self.red_objects = []
      self.blue_objects = []
      self.gathered = 0
      self.stacked = False
      self.returned = False
      self.x = 0
      self.y = 0
      self.orientation = 0
      print('...Success.')
    except Exception:
      print('...Failure.')

  ## Capture image then identify target objects.
  def use_camera(self):
    (success, frame) = self.camera.read()
    raw = Image.fromarray(frame)
    BGR = raw.split()
    B = array(BGR[0].getdata(), dtype=float32)
    G = array(BGR[1].getdata(), dtype=float32)
    R = array(BGR[2].getdata(), dtype=float32)
    NDI_G = ((BIAS)*G)/(R+B+MINIMUM)
    NDI_R = ((BIAS)*R)/(G+B+MINIMUM)
    NDI_B = ((BIAS)*B)/(R+G+MINIMUM)
    # Reshape
    green_image = NDI_G.reshape(HEIGHT,WIDTH)
    blue_image = NDI_B.reshape(HEIGHT,WIDTH)
    red_image = NDI_R.reshape(HEIGHT,WIDTH)
    # Columns
    green_columns = green_image.sum(axis=0)
    blue_columns = blue_image.sum(axis=0)
    red_columns = red_image.sum(axis=0)
    # Threshold
    green_threshold = numpy.mean(green_columns) #+ numpy.std(green_columns)
    red_threshold = numpy.mean(red_columns) #+ numpy.std(red_columns)
    blue_threshold = numpy.mean(blue_columns) #+ numpy.std(blue_columns)
    # Green
    x = 0
    self.green_objects = []
    while (x < WIDTH-1):
      if (green_columns[x] > green_threshold):
        start = x
        while (green_columns[x] > green_threshold) and (x < WIDTH-1):
          x += 1
        end = x
        size = (end - start)
        offset = (start + (end - start)/2) - CENTER
        self.green_objects.append((size,offset))
      else:
        x += 1
    # Red
    x = 0
    self.red_objects = []
    while (x < WIDTH-1):
      if (red_columns[x] > red_threshold):
        start = x
        while (red_columns[x] > red_threshold) and (x < WIDTH-1):
          x += 1
        end = x
        size = (end - start)
        offset = (start + (end - start)/2) - CENTER
        self.red_objects.append((size,offset))
      else:
        x += 1
    # Blue
    x = 0
    self.blue_objects = []
    while (x < WIDTH-1):
      if (blue_columns[x] > blue_threshold):
        start = x
        while (blue_columns[x] > blue_threshold) and (x < WIDTH-1):
          x += 1
        end = x
        size = (end - start)
        offset = (start + (end - start)/2) - CENTER # from center
        self.blue_objects.append((size,offset))
      else:
        x += 1

  ## Connect to Server.
  def connect(self):
    if (self.connected_out == False) and (self.connected_in == False):
      try:
        print('Establishing SEND Port to Server...')
        self.socket_out = socket.socket(AF_INET, SOCK_STREAM)
        self.socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
    else:
      print('ALREADY CONNECTED')
  
  ## Disconnect from Server.
  def disconnect(self):
    try:
      print('Disconnecting from Server...')
      self.socket_in.close()
      self.socket_out.close()
      self.connection.close()
      print('...Success')
    except Exception:
      print('...Failure')
      pass
  
  ## Receives COMMAND from Server.
  def receive_command(self):
    try: 
      print('Receiving COMMAND...')
      json_command = self.socket_in.recv(BUFFER_SIZE)
      dict_command = json.loads(json_command)
      self.command = dict_command['COMMAND']
      print(str(json_command))
      print('...Success.')
    except socket.error as SocketError:
      print('...Connection Failure.')
  
  ## Send RESPONSE to Server
  def send_response(self):   
    try:
      print('Sending ACTION...')
      json_response = json.dumps({'ACTION':self.action})
      self.connection.send(json_response)
      print(str(json_response))
      print("...Success.")
    except Exception:
      print("...Failure.")

  ## After receiving COMMAND, determine action.
  def decide_action(self):
    if (self.command == 'START') or (self.command == 'CONTINUE'):
      self.use_camera()
      """
      THE BRAIN
      """
      if (self.gathered < 4):
        (size,offset) = max(self.green_objects)
        print(max(self.green_objects))
        if (offset > 0 + THRESHOLD):
          self.action = 'RIGHT'
          self.orientation += TURN
        elif (offset < 0 - THRESHOLD):
          self.action = 'LEFT'
          self.orientation -= TURN
        else:
          if (size > RANGE):
            self.action = 'GRAB'
            self.gathered += 1
            print('Gathered: ' + str(self.gathered))
          else:
            self.action = 'FORWARD'
            self.x += TRAVEL*cos(self.orientation)
            self.y += TRAVEL*sin(self.orientation)
      elif (not self.stacked):
        self.action = 'STACK'
        self.stacked = True
      elif (not self.returned):
        self.action = 'BACKWARD'
        self.returned = True
      else:
        self.action = 'WAIT'
    elif (self.command == 'STOP') or (self.command == 'PAUSE'):
      self.action == 'WAIT'
    elif (self.command == 'DISCONNECT'):
      self.action = 'WAIT'
      self.connected_in = False
      self.connected_out = False
      self.disconnect()
    else:
      self.action = 'UNKNOWN'
    self.control_arduino()
    self.previous_actions.append(self.action)
    print(self.previous_actions)
    print(self.x)
    print(self.y)

  ## Execute action with arduino.
  def control_arduino(self):
    try:
      self.arduino.write(self.action)
      self.status = self.arduino.readline()
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

# Main
if __name__ == "__main__":
  Worker = BOSS_Worker()
  while 1:
    Worker.connect()
    while (Worker.connected_in) or (Worker.connected_out):
      Worker.receive_command()
      Worker.decide_action()
      Worker.send_response()
    else:
      Worker.disconnect()
