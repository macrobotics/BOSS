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
CAMERA_LEVEL = CAMERA_HEIGHT/2.0
CAMERA_THRESHOLD = CAMERA_WIDTH/8.0
SIZE_GRAB_RANGE = CAMERA_WIDTH/4.0
BIAS = 10.0
MINIMUM_COLOR = 0.01
MINIMUM_SIZE = CAMERA_WIDTH/64.0
MAX_CONNECTIONS = 5
TURN = pi/16.0 # in radians
TRAVEL = 0.5
ZONE_X = 8.0
ZONE_Y = 8.0
START_X = 0.0
START_Y = 0.0
DP = 6 
MIN_DISTANCE = CAMERA_CENTER
EDGE_THRESHOLD = 40 # param1
CENTER_THRESHOLD = 20 # param2
MIN_RADIUS = 10
MAX_RADIUS = 20

# Error Messages
ERROR_NONE = 0
ERROR_PARSE = 254
ERROR_CONNECTION = 255
ERROR_CLOSE = 1
ERROR_FAR = 2
ERROR_LOAD = 3
ERROR_ACTION = 4
ERROR_BLOCKED = 5
ERROR_ORBIT_RIGHT = 6
ERROR_ORBIT_LEFT = 7
ERROR_AVOID_RIGHT = 8
ERROR_AVOID_LEFT = 9

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

    self.reset_worker()

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
      if ((abs(CAMERA_CENTER - x) < CAMERA_THRESHOLD) and (abs(CAMERA_LEVEL - y) < CAMERA_THRESHOLD)):  
        return True
      else:
        return False
    except TypeError:
      return False

  ## Connect to Server.
  def connect(self):
    if (self.connected_out == False) and (self.connected_in == False):
      try:
        self.socket_out = socket.socket(AF_INET, SOCK_STREAM)
        self.socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_out.bind((ADDRESS_OUT))
        self.socket_out.listen(QUEUE_MAX)
        (self.connection, self.address) = self.socket_out.accept()
        self.connected_out = True
        message = 'Success.'
      except socket.error as message:
        message = 'Failure.'
        self.connected_out = False
        self.socket_out.close()
        pass
      print('[Establishing Send Port]...' + str(message))
      try:
        self.socket_in = socket.socket(AF_INET,SOCK_STREAM)
        self.socket_in.connect((ADDRESS_IN))
        self.connected_in = True
        message = 'Success.'
      except socket.error as message:
        self.socket_in.close()
        self.connected_in = False
        pass
      print('[Establishing Receive Port]...' + str(message))
  
  ## Receives COMMAND from Server.
  def receive_command(self):
    try: 
      json_command = self.socket_in.recv(BUFFER_SIZE)
      dict_command = json.loads(json_command)
      self.command = dict_command['COMMAND']
      message = str(json_command)
    except socket.error as message:
      pass #!
    print('----------------------------------')
    print('[Receiving COMMAND]...' + str(message))

  ## After receiving COMMAND, determine action.
  def decide_action(self):
    if (self.command == 'START'):
      self.goal = 'STARTING'
      self.start()
    elif (self.command == 'CONTINUE'):
      if (self.gathered < 4):
        self.goal = 'GATHERING'
        self.gather()
      elif (not self.dumped):
        self.goal = 'STACKING'
        self.find_zone()
      elif (not self.returned):
        self.goal = 'RETURNING'
        self.return_home()
      else:
        self.action = 'W'
    elif (self.command == 'PAUSE'):
      self.action = 'W'
    elif (self.command == 'DISCONNECT'):
      self.action = 'W'
      self.disconnect()
    else:
      self.action = 'W'

  ## Start Logic
  def start(self):
    self.action = 'H'
    print('[Starting]...Helping Extend Rack.')

  ## Gather Logic
  def gather(self):
    objects = self.detect_objects()
    #1 There is an object in view...
    try:
      (size, offset) = max(objects)
      #2 ...and I was just trying to turn...
      if (self.error_number == 5):
        #3 ...left.
        for previous_action in ['T','S','R','Q']:
          if (self.previous_action == previous_action):
            message = 'Blocked After Turning Right -> Avoiding Left.'
            self.action = 'J'
        #3 ...right.
        for previous_action in ['K','L','M','N']:
          if (self.previous_action == previous_action):
            message = 'Blocked After Turning Left --> Avoiding Right.'
            self.action = 'I' #!
      #2 ...and I wasn't just trying to grab something...
      elif not (self.error_number == 3):
        #3 ...and it's to the right.
        if (offset > CAMERA_THRESHOLD):
          if (offset > 4*CAMERA_THRESHOLD):
            message = '(Object in View -> 4 Right.'
            self.action = 'T'
            self.orientation += 4*TURN
          elif (offset > 3*CAMERA_THRESHOLD):
            message = 'Object in View -> 3 Right.'
            self.action = 'S'
            self.orientation += 3*TURN
          elif (offset > 2*CAMERA_THRESHOLD):
            message = 'Object in View -> 2 Right.'
            self.action = 'R'
            self.orientation += 2*TURN
          else:
            message = 'Object in View -> 1 Right'
            self.action = 'Q'
            self.orientation += 1*TURN
        #3 ...and it's to the left.
        elif (offset < -CAMERA_THRESHOLD):
          if (offset < -4*CAMERA_THRESHOLD):
            message = 'Object in View -> 4 Left'
            self.action = 'N'
          elif (offset < -3*CAMERA_THRESHOLD):
            message = 'Object in View -> 3 Left'
            self.action = 'M'
          elif (offset < -2*CAMERA_THRESHOLD):
            message = 'Object in View -> 2 Left'
            self.action = 'L'
          else:
            message = 'Object in View -> 1 Left'
            self.action = 'K'
        #3 ...and it is straight ahead.
        else:
          #4 ...and it is too small to be close.
          if (size < SIZE_GRAB_RANGE):
            message = 'Too Small -> Out of Range'
            self.action = 'F'
          #4 ...and it is big enough to be close.
          else:
            #5 ...and it is oriented.
            if (self.is_oriented()):
              message = 'Large Enough -> In Range, Oriented -> Grab'
              self.action = 'G'
              self.gathered += 1 #!
            #5 ...but it isn't oriented...
            else:
              #6  ... and I didn't just try to go around right.
              if not (self.error_number == 6):
                message = 'Large Enough -> In Range, Not Oriented --> Orbiting Right.'
                self.action = 'O'
              #6 ... and I didn't just try to go around left.
              elif not (self.error_number == 7):
                message = 'Large Enough -> In Range, Not Oriented & Blocked Right -> Orbiting Left.'
                self.action = 'P'
      #2 ...and I was already trying to grab something.
      elif (self.error_number == 3):
        message = 'Load Failed -> Reversing.'
        self.action = 'B'
      #2 ...but I don't know what to do.
      else:
        message = 'Confused -> Waitiing.'
        self.action = 'W'
    #1 There are no objects in view.
    except ValueError:
      message = 'No Objects Detected -> Searching Right.'
      self.action = 'T'
    
    print('[Gathering]...' + str(objects) + '...' + message)
    print('[Remembering Action]...' )
    self.previous_action = self.action # remember newest action

  ## Find Zone
  def find_zone(self):
    #1 Not at the zone...
    if not ((int(self.x) == ZONE_X) and (int(self.y) == ZONE_Y)):
      #2 Clockwise from Zone...
      if (self.orientation > tan((ZONE_Y - self.y)/(ZONE_X - self.x)) + TURN): #!
        message = 'Clockwise from Zone -> Turning Left.'
        self.action = 'L'
        self.orientation -= TURN
      #2 Counter-clockwise from Zone...
      elif (self.orientation < tan((ZONE_Y - self.y)/(ZONE_X - self.x)) - TURN): #!
        message = 'Counter-clockwise from Zone -> Turning Right.'
        self.action = 'R'
        self.orientation += TURN
      #2 Facing Zone...
      else:
        if (self.error_number == 1):
          message = 'Path Blocked -> Avoiding Right.'
          self.action = 'I'
        else:     
          message = 'Facing Zone -> Moving Forward.'
          self.action = 'F'
          self.x += TRAVEL*cos(self.orientation) #!
          self.y += TRAVEL*sin(self.orientation) #!
    #1 Reached zone...
    else:  
      message = 'At Zone -> Dumping Bales.'
      self.action = 'D'
      self.dumped = True #!
    print('[Finding Zone]...' + str((self.x, self.y, self.orientation)) + '...' + message)
  
  ## Return Home
  def return_home(self):
    #1 I'm not at home...
    if not ((int(self.x) == START_X) and (int(self.y) == START_Y)):
      #2 ...and I am clockwise from home...
      if (self.orientation > tan((START_Y - self.y)/(START_X - self.x)) + RADIANS_TURN): #!
        message = 'Clockwise from Home -> Turning Left.'
        self.action = 'L'
        self.orientation -= TURN
      #2 ...and I am counter-clockwise from home...
      elif (self.orientation < tan((ZONE_Y - self.y)/(ZONE_X - self.x)) - RADIANS_TURN): #!
        message = 'Counter-clockwise from Home -> Turning Right.'
        self.action = 'R'
        self.orientation += TURN
      #2 ..and I am facing home...
      else:
        #3 ...but not blocked.
        if not (error_number == 1):
          message = 'Facing Home -> Moving Forward.'
          self.action = 'F'
          self.x += TRAVEL*cos(self.orientation) #!
          self.y += TRAVEL*sin(self.orientation) #!
        #3 ...but am blocked.
        else:
          message = 'Path Blocked -> Avoiding Right.'
          self.action = 'I'
    #1 I've reached home.
    else:
      self.action = 'W'
      self.returned = True #!
    print('[Returning]...' + '(' + str(self.x) + ',' + str(self.y) + ')' + '...' + message)

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
      self.gathered -= 1
    elif (self.error_number == ERROR_LOAD):
      self.error = 'LOAD FAILED'
      self.gathered -= 1
    elif (self.error_number == ERROR_PARSE):
      self.error = 'PARSE FAILED'
    elif (self.error_number == ERROR_ACTION):
      self.error = 'BAD ACTION'
    elif (self.error_number == ERROR_BLOCKED):
      self.error = 'BLOCKED AFTER TURN'
    elif (self.error_number == ERROR_ORBIT_RIGHT):
      self.error = 'ORBIT RIGHT FAILED'
    elif (self.error_number == ERROR_ORBIT_LEFT):
      self.error = 'ORBIT LEFT FAILED'
    elif (self.error_number == ERROR_AVOID_RIGHT):
      self.error = 'AVOID RIGHT FAILED'
    elif (self.error_number == ERROR_AVOID_LEFT):
      self.error = 'AVOID LEFT FAILED'
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
      self.reset_worker()
      message = 'Success.'
    except Exception:
      message = 'Failure.'
      pass
    print('[Disconnecting]...' + message)

  ## Reset Worker
  def reset_worker(self):
    try:
      self.connected_out = False
      self.connected_in = False
      self.command = None
      self.response = None
      self.action = None
      self.previous_action = None
      self.error = None
      self.error_number = None
      self.gathered = 0
      self.dumped = False
      self.returned = False
      self.x = 0
      self.y = 0
      self.orientation = 0
      message = 'Success.'
    except Exception:
      message = 'Failure.'
    print('[Resetting Worker]...' + message)
    
# Main
if __name__ == "__main__":
  green = Worker()
  while True:
    time.sleep(1)
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
