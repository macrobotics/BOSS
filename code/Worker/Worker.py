#!/usr/bin/python
# Worker.py
# MacRobotics

# Imports
from serial import SerialException
from socket import *
from numpy import *
from PIL import Image 
from cv2 import VideoCapture
from time import *
import cv2, cv
import numpy
import socket
import time
import json
import serial
import sys
import ast
import subprocess

# Setup
ADDRESS_IN = ('10.42.0.1',50000) # 10.42.0.1
ADDRESS_OUT = ('10.42.0.3',50001) # 10.42.0.3
BUFFER_SIZE = 4096
QUEUE_MAX = 5
BAUD = 9600
DEVICE = '/dev/ttyS0' # '/dev/ttyS0' for AlaMode, '/dev/ttyAMC0' for Uno
CAMERA_INDEX = 0
CAMERA_WIDTH = 320.0
CAMERA_HEIGHT = 240.0
CAMERA_CENTER = CAMERA_WIDTH/2.0
CAMERA_THRESHOLD = CAMERA_WIDTH/8.0
ERROR = pi/32.0
RANGE = CAMERA_WIDTH/1.5
BIAS = 100.0
MINIMUM_COLOR = 0.01
MINIMUM_SIZE = CAMERA_WIDTH/32.0
MAX_CONNECTIONS = 5
TURN = pi/16.0
TRAVEL = 0.5
ZONE_X = 8.0
ZONE_Y = 8.0
START_X = 0.0
START_Y = 0.0
ERROR_NONE = 0
ERROR_PARSE = 254
ERROR_CONNECTION = 255
ERROR_CLOSE = 1
ERROR_FAR = 2
ERROR_LOAD = 3
ERROR_ACTION = 4
DP = 6 
MIN_DISTANCE = CAMERA_CENTER
EDGE_THRESHOLD = 40 # param1
CENTER_THRESHOLD = 20 # param2
MIN_RADIUS = 10
MAX_RADIUS = 20

# Class Worker
class Worker:

  ## Initialize Worker robot.
  def __init__(self):
    try:
      self.camera = VideoCapture(CAMERA_INDEX)
      self.camera.set(3,CAMERA_WIDTH)
      self.camera.set(4,CAMERA_HEIGHT)
      message = 'Success.'
    except Exception:
      message = 'Failure.'
    print('[Setting up Camera]...' + message)

    try:
      self.arduino = serial.Serial(DEVICE, BAUD)
      message = 'Success.'
    except Exception:
      message = 'Failure.'
    print('[Setting up Controller]...' + message)

    try:
      self.connected_out = False
      self.connected_in = False
      self.command = None
      self.response = None
      self.action = None
      self.error = None
      self.error_number = None
      self.gathered = 0
      self.stacked = False
      self.returned = False
      self.x = 0
      self.y = 0
      self.orientation = 0
      message = 'Success.'
    except Exception:
      message = 'Failure.'
    print('[Initializing Worker]...' + message)

  ## Capture image then identify target objects.
  def detect_objects(self):
    objects = []
    x = 0
    for cache in range(10):
      (success, frame) = self.camera.read()
    raw = Image.fromarray(frame)
    BGR = raw.split()
    B = array(BGR[0].getdata(), dtype=float32)
    G = array(BGR[1].getdata(), dtype=float32)
    R = array(BGR[2].getdata(), dtype=float32)
    NDI_G = (BIAS*G + MINIMUM_COLOR)/(R + B + MINIMUM_COLOR)
    matrix = NDI_G.reshape(CAMERA_HEIGHT,CAMERA_WIDTH)
    columns = matrix.sum(axis=0)
    high = numpy.mean(columns) + numpy.std(columns)
    low = numpy.mean(columns)
    while (x < CAMERA_WIDTH-1):
      if (columns[x] > high):
        start = x
        while (columns[x] > low) and (x < CAMERA_WIDTH-1):
          x += 1
        end = x
        size = (end - start)
        offset = (start + (end - start)/2) - CAMERA_CENTER
        if (size > MINIMUM_SIZE):
          objects.append((size,offset))
      else:
        x += 1
    return objects

  ## Is Oriented? --> Boolean
  def is_oriented(self):
    for cache in range(10):
      (success, frame) = self.camera.read()
    grayscale = cv2.cvtColor(frame, cv.CV_BGR2GRAY)
    blurred = cv2.GaussianBlur(grayscale, (0,0), 5) # (0,0), 5
    colored = cv2.cvtColor(blurred,cv2.COLOR_GRAY2BGR)
    (flag, thresholded) = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY) # 50 and 255 WORKS
    circles = cv2.HoughCircles(thresholded,cv2.cv.CV_HOUGH_GRADIENT,DP,MIN_DISTANCE,param1=EDGE_THRESHOLD, param2=CENTER_THRESHOLD, minRadius=MIN_RADIUS,maxRadius=MAX_RADIUS)
    try:
      for target in circles[0,:]:
        x = target[0]
        y = target[1]
        r = target[2]
      if (abs(CAMERA_CENTER - x) > CAMERA_THRESHOLD):  
        return False
      else:
        return True
    except TypeError:
      print('Not Oriented')
      return False

  ## Connect to Server.
  def connect(self):
    if (self.connected_out == False) and (self.connected_in == False):
      try:
        self.socket_out = socket.socket(AF_INET, SOCK_STREAM)
        self.socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_out.bind((ADDRESS_OUT))
        self.socket_out.listen(QUEUE_MAX)
        (self.connection,self.address) = self.socket_out.accept()
        self.connected_out = True
        message = 'Success.'
      except socket.error as SocketError:
        message = 'Failure.'
        self.connected_out = False
        self.socket_out.close()
        pass
      print('[Establishing Send Port]...' + message)
      try:
        self.socket_in = socket.socket(AF_INET,SOCK_STREAM)
        self.socket_in.connect((ADDRESS_IN))
        self.connected_in = True
        message = 'Success.'
      except socket.error as error:
        self.socket_in.close()
        self.connected_in = False
        message = 'Failure.'
        pass
      print('[Establishing Receive Port]...' + message)
  
  ## Receives COMMAND from Server.
  def receive_command(self):
    try: 
      json_command = self.socket_in.recv(BUFFER_SIZE)
      dict_command = json.loads(json_command)
      self.command = dict_command['COMMAND']
      message = str(json_command)
    except socket.error as SocketError:
      message = 'Connection Failure.'
    print('[Receiving COMMAND]...' + message)

  ## After receiving COMMAND, determine action.
  def decide_action(self):
    if (self.command == 'START') or (self.command == 'CONTINUE'):
      if (self.gathered < 4):
        self.goal = 'GATHERING'
        self.gather()
      elif (not self.stacked):
        self.goal = 'STACKING'
        self.stack()
      elif (not self.returned):
        self.goal = 'RETURNING'
        self.return_home()
      else:
        self.action = 'W'
    elif (self.command == 'STOP'):
      self.action = 'W'
    elif (self.command == 'PAUSE'):
      self.action = 'W'
    elif (self.command == 'DISCONNECT'):
      self.action = 'W'
      self.disconnect()
    else:
      self.action = 'W'

  ## Gather Logic
  def gather(self):
    objects = self.detect_objects()
    try:
      (size, offset) = max(objects)
      if (offset > CAMERA_THRESHOLD):
        if (offset > 2*CAMERA_THRESHOLD):
          message = 'Target to Far Right'
          self.action = 'T'
          self.orientation += TURN #!
        else:
          message = 'Target to Right'
          self.action = 'R'
          self.orientation += TURN #!
      elif (offset < -CAMERA_THRESHOLD):
        if (offset < -2*CAMERA_THRESHOLD):
          message = 'Target to Far Left'
          self.action = 'M'
          self.orientation -= TURN #!
        else:
          message = 'Target to Left'
          self.action = 'L'
          self.orientation += TURN #!
      elif (self.is_oriented()):
        if (size > RANGE):
          message = 'Target in Grab Range'
          self.action = 'G'
          self.gathered += 1 #!
        elif (not self.error_number == ERROR_CLOSE):
          message = 'Target out of Grab Range'
          self.action = 'F'
          self.x += TRAVEL*cos(self.orientation) #!
          self.y += TRAVEL*sin(self.orientation) #!
        else:
          message = 'Object in Way'
          self.action = 'R'
          self.orientation += TURN #!
      else:
        message = 'Target Not Oriented'
        self.action = 'R'
        self.orientation += TURN #!
    except ValueError:
      message = 'No Objects Detected'
      self.action = 'W'
    print('[Deciding Action]...' + self.goal + '...' + message)

  ## Stack Logic
  def stack(self):
    if (not (int(self.x) == ZONE_X and int(self.y) == ZONE_Y)):
      if (self.orientation > tan((ZONE_Y - self.y)/(ZONE_X - self.x)) + ERROR): #!
        self.action = 'L'
        self.orientation -= TURN
      elif (self.orientation < tan((ZONE_Y - self.y)/(ZONE_X - self.x)) - ERROR): #!
        self.action = 'R'
        self.orientation += TURN
      else:
        self.action = 'F'
        self.x += TRAVEL*cos(self.orientation) #!
        self.y += TRAVEL*sin(self.orientation) #!
    else:  
      self.action = 'S'
      self.stacked = True #!

  def return_home(self):
    if (not (int(self.x) == START_X and int(self.y) == START_Y)):
      if (self.orientation > tan((START_Y - self.y)/(START_X - self.x)) + ERROR): #!
        self.action = 'L'
        self.orientation -= TURN
      elif (self.orientation < tan((ZONE_Y - self.y)/(ZONE_X - self.x)) - ERROR): #!
        self.action = 'R'
        self.orientation += TURN
      else:
        self.action = 'F'
        self.x += TRAVEL*cos(self.orientation) #!
        self.y += TRAVEL*sin(self.orientation) #!
    else:
      self.action = 'W'
      self.returned = True #!

  ## Execute action with arduino.
  def control_arduino(self):

    ### Send
    try:
      self.arduino.write(self.action)
      message = self.action
    except Exception:
      message = 'Failure.'
    print('[Sending ACTION]...' + message)

    ### Receive
    try:
      self.error_number = int(self.arduino.readline())
      message = str(self.error_number)
    except ValueError:
      self.error_number = ERROR_PARSE
      message = "ValueError: Failed to parse signal, retrying..."
    except OSError:
      self.error_number = ERROR_CONNECTION
      message = "OSError: Connection lost, retrying..."
    except SerialException:
      self.error_number = ERROR_CONNECTION
      message = "Serial Exception: Connection lost, retrying..."
    except SyntaxError:
      self.error_number = ERROR_PARSE
      message = "Syntax Error: Failed to parse signal, retrying..."
    except KeyError:
      self.error_number = ERROR_PARSE
      message = 'KeyError: Failed to parse signal, retrying...'
    print('[Receiving ERROR from Controller]...' + message)

  ## Handle Errors from Arduino
  def handle_error(self):
    if (self.error_number == ERROR_NONE):
      self.error = 'NONE'
    elif (self.error_number == ERROR_CLOSE):
      self.error = 'TOO CLOSE'
    elif (self.error_number == ERROR_FAR):
      self.error = 'TOO FAR'
    elif (self.error_number == ERROR_LOAD):
      self.error = 'LOAD FAILED'
      self.gathered -= 1
    elif (self.error_number == ERROR_PARSE):
      self.error = 'PARSE FAILED'
    elif (self.error_number == ERROR_ACTION):
      self.error = 'BAD ACTION'
    else:
      self.error = 'UNKNOWN ERROR'
    print('[Handling ERRORS]...' + self.error)

  ## Send RESPONSE to Server
  def send_response(self):   
    try:
      json_response = json.dumps({'ACTION':self.action, 'ERROR':self.error, 'GATHERED':str(self.gathered), 'GOAL':self.goal})
      self.connection.send(json_response)
      message = str(json_response)
    except Exception:
      message = "Failure."
    print('[Sending RESPONSE]...' + message)

  ## Disconnect from Server.
  def disconnect(self):
    try:
      self.socket_in.close()
      self.socket_out.close()
      self.connection.close()
      self.connected_in = False
      self.connected_out = False
      message = 'Success.'
    except Exception:
      message = 'Failure.'
      pass
    print('[Disconnecting]...' + message)

# Main
if __name__ == "__main__":
  green = Worker()
  while 1:
    green.connect()
    while (green.connected_in) or (green.connected_out):
      green.receive_command()
      green.decide_action()
      green.control_arduino()
      green.handle_error()
      if (green.connected_in == False) or (green.connected_out == False):
        break
      else:
        green.send_response()
    else:
      green.disconnect()
