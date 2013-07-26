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
ADDRESS_IN = ('10.42.0.1',40000) # 10.42.0.1
ADDRESS_OUT = ('10.42.0.3',40001) # 10.42.0.3
BUFFER_SIZE = 4096
QUEUE_MAX = 5
BAUD = 9600
DEVICE = '/dev/ttyS0' # '/dev/ttyS0' for AlaMode, '/dev/ttyAMC0' for Uno
CAMERA_INDEX = 0
CAMERA_WIDTH = 320.0
CAMERA_HEIGHT = 240.0
CAMERA_CENTER = CAMERA_WIDTH/2.0
CAMERA_LEVEL = CAMERA_HEIGHT/2.0
CAMERA_THRESHOLD = CAMERA_WIDTH/12.0
SIZE_GRAB_RANGE = CAMERA_WIDTH/4.0
SIZE_ZONE_RANGE = CAMERA_WIDTH/3.0
SIZE_HOME_RANGE = CAMERA_WIDTH/3.0
BIAS = 10.0
MINIMUM_COLOR = 0.01
MINIMUM_SIZE = CAMERA_WIDTH/64.0
MAX_CONNECTIONS = 5
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
ERROR_ACTION = 1
ERROR_CLOSE = 2
ERROR_LOAD = 3
ERROR_BLOCKED_RIGHT = 4
ERROR_BLOCKED_LEFT = 5
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

  ## Capture image then identify Home.
  def detect_green(self):
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

  ## Detect 
  def detect_yellow(self):
    objects = []
    x = 0
    for cache in range(30):
      (success, frame) = self.camera.read()
    raw = Image.fromarray(frame)
    BGR = raw.split()
    B = array(BGR[0].getdata(), dtype=float32)
    G = array(BGR[1].getdata(), dtype=float32)
    R = array(BGR[2].getdata(), dtype=float32)
    NDI_G = BIAS*(G + R + MINIMUM_COLOR)/(2*B + MINIMUM_COLOR)
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
      if (abs(CAMERA_CENTER - x) < CAMERA_THRESHOLD):  
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
      elif (not self.returning):
        self.goal = 'RETURNING'
        self.return_home()
      else:
        self.action = 'W'
    elif (self.command == 'PAUSE'):
      self.goal = 'PAUSING'
      self.action = 'W'
    elif (self.command == 'DISCONNECT'):
      self.goal = 'DISCONNECTING'
      self.action = 'W'
    else:
      self.action = 'W'

  ## Start Logic
  def start(self):
    self.action = 'H'
    print('[Starting]...Helping Extend Rack.')

  ## Gather Logic
  def gather(self):
    objects = self.detect_green()
    #1 There is an object in view...
    try:
      (size, offset) = max(objects)
      #2 ...and it is small...
      if (size < SIZE_GRAB_RANGE) and not (self.error_number == ERROR_LOAD):
        #3 ...and I just tried avoiding to the left...
        if (self.error_number == ERROR_AVOID_RIGHT):
            message = 'Blocked After Avoiding Right -> Avoiding Left.'
            self.action = 'J'
        #3 ...and I just tried avoid to the right...
        elif (self.error_number == ERROR_AVOID_LEFT):
          message = 'Blocked After Avoiding Left --> Avoiding Right.'
          self.action = 'I'
        #3 ...and I just tried to turn right...
        elif (self.error_number == ERROR_BLOCKED_LEFT):
          message = 'Blocked After Turning Left --> Avoiding Right.'
          self.action = 'I'
        #3 ... and i just tried to turn left...
        elif (self.error_number == ERROR_BLOCKED_LEFT):
          message = 'Blocked After Turning Right --> Avoiding Left.'
          self.action = 'J'
        #3 ...and I just was blocked after moving...
        elif (self.error_number == ERROR_CLOSE):
          message = 'Blocked After Turning Right --> Avoiding Left.'
          self.action = 'I'         
        #3 ...and I didn't make bad movements...
        else:
          #4 ...and it's to the right...
          if (offset > CAMERA_THRESHOLD):
            if (offset > 4*CAMERA_THRESHOLD):
              message = '(Object in View -> 4 Right.'
              self.action = 'T'
            elif (offset > 3*CAMERA_THRESHOLD):
              message = 'Object in View -> 3 Right.'
              self.action = 'S'
            elif (offset > 2*CAMERA_THRESHOLD):
              message = 'Object in View -> 2 Right.'
              self.action = 'R'
            else:
              message = 'Object in View -> 1 Right'
              self.action = 'Q'
          #4 ...and it's to the left.
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
          #4 ...and it's in front...
          else:
            message = 'Too Small -> Out of Range'
            self.action = 'F'
      #2 ...and it is large...
      elif (size > SIZE_GRAB_RANGE):
        #3 ...and I was just trying to grab something...
        if (self.error_number == ERROR_LOAD):
          message = 'Load Failed -> Reversing.'
          self.action = 'B'
        #3 ...and I was not just trying to grab something...
        else:
          #4 ...and it is oriented...
          if True: #! (self.is_oriented())
              message = 'Large Enough -> In Range, Oriented -> Grab'
              self.action = 'G'
              self.gathered += 1
          #4 ...but it is not oriented..
          else:
            #5 ...and I already tried to orbit left.
            if (self.error_number == ERROR_ORBIT_LEFT):
              message = 'Large Enough -> In Range, Not Oriented --> Orbiting Right.'
              self.action = 'O'
            #5 ...and I didn't just try to go around right.
            elif (self.error_number == ERROR_ORBIT_RIGHT):
              message = 'Large Enough -> In Range, Not Oriented & Blocked Right -> Orbiting Left.'
              self.action = 'P'
            #5 ... grab anyway.
            else:
              message = 'In Range, Not Oriented -> Attempting to Orbing .'
              self.action = 'O'  
      #2
      else:
        self.action = 'W'
        message = 'Confused -> Waiting.'    
    #1 There are no objects in view.
    except ValueError:
      message = 'No Objects Detected -> Searching Right.'
      self.action = 'T'
    
    print('[Gathering]...' + str(objects) + '...' + message)
    print('[Remembering Action]...' )
    self.previous_action = self.action # remember newest action

  ## Find Zone
  def find_zone(self):
    objects = self.detect_green()
    # The Zone is in view...
    try:
      (size, offset) = max(objects)
      #2 ... but not at the zone...
      if (size < SIZE_HOME_RANGE):
        #3 ... and it's to the right.
        if (offset > CAMERA_THRESHOLD):
          if (offset > 4*CAMERA_THRESHOLD):
            message = '(Zone in View -> 4 Right.'
            self.action = 'T'
          elif (offset > 3*CAMERA_THRESHOLD):
            message = 'Zone in View -> 3 Right.'
            self.action = 'S'
          elif (offset > 2*CAMERA_THRESHOLD):
            message = 'Zone in View -> 2 Right.'
            self.action = 'R'
          else:
            message = 'Zone in View -> 1 Right'
            self.action = 'Q'
        #3 ...and it's to the left.
        elif (offset < -CAMERA_THRESHOLD):
          if (offset < -4*CAMERA_THRESHOLD):
            message = 'Zone in View -> 4 Left'
            self.action = 'N'
          elif (offset < -3*CAMERA_THRESHOLD):
            message = 'Zone in View -> 3 Left'
            self.action = 'M'
          elif (offset < -2*CAMERA_THRESHOLD):
            message = 'Zone in View -> 2 Left'
            self.action = 'L'
          else:
            message = 'Zone in View -> 1 Left'
            self.action = 'K'
        #3 ...and it is straight ahead.
        else:
          #4 ...but it is blocked ahead.
          if (self.error_number == ERROR_CLOSE):
            message = 'Object in Way -> Avoiding Right.'
            self.action = 'I'
          #4 ...but it is blocked after turning right.
          elif (self.error_number == ERROR_AVOID_RIGHT):
            message = 'Failed to Turn Right -> Avoiding Left.'
            self.action = 'J'
          #4 ...but it is blocked after avoiding right.
          elif (self.error_number == ERROR_AVOID_RIGHT):
            message = 'Failed to Avoid Right -> Avoiding Left.'
            self.action = 'J'
          #4 ...but it is blocked to the left.
          elif (self.error_number == ERROR_BLOCKED_LEFT):
            message = 'Failed to Turn Left -> Avoiding Right.'
            self.action = 'I'
          #4 ...but it is blocked after avoiding right.
          elif (self.error_number == ERROR_BLOCKED_RIGHT):
            message = 'Failed to Avoid Left -> Avoiding Right.'
            self.action = 'I'
          #4 ...and isn't blocked.
          else:
            message = 'Zone Too Small -> Moving Forward.'
            self.action = 'F'
      #2 ..and have reached the zone.
      else:  
        message = 'At Zone -> Dumping Bales.'
        self.action = 'D'
        self.dumped = True
    #1 The Zone is not in view...
    except ValueError:
        message = 'Cannot See Zone -> Searching Left For Zone.'
        self.action = 'N'
    print('[Finding Zone]...' + message)
  
  ## Return Home
  def return_home(self):
    objects = self.detect_yellow()
    #1 Home is in view...
    try:
      (size, offset) = max(objects)
      #2 ... but not at the home...
      if (size < SIZE_ZONE_RANGE):
        #3 ... and it's to the right.
        if (offset > CAMERA_THRESHOLD):
          if (offset > 4*CAMERA_THRESHOLD):
            message = 'Home in View -> 4 Right.'
            self.action = 'T'
          elif (offset > 3*CAMERA_THRESHOLD):
            message = 'Home in View -> 3 Right.'
            self.action = 'S'
          elif (offset > 2*CAMERA_THRESHOLD):
            message = 'Home in View -> 2 Right.'
            self.action = 'R'
          else:
            message = 'Home in View -> 1 Right'
            self.action = 'Q'
        #3 ...and it's to the left.
        elif (offset < -CAMERA_THRESHOLD):
          if (offset < -4*CAMERA_THRESHOLD):
            message = 'Home in View -> 4 Left'
            self.action = 'N'
          elif (offset < -3*CAMERA_THRESHOLD):
            message = 'Home in View -> 3 Left'
            self.action = 'M'
          elif (offset < -2*CAMERA_THRESHOLD):
            message = 'Home in View -> 2 Left'
            self.action = 'L'
          else:
            message = 'Home in View -> 1 Left'
            self.action = 'K'
        #3 ...and it is straight ahead.
        else:
          #4 ...but it is blocked.
          if ((self.error_number == ERROR_BLOCKED_LEFT) or (self.error_number == ERROR_CLOSE) or (self.error_number == ERROR_AVOID_LEFT)):
            message = 'Object in Way Failed to go Left -> Avoiding Right.'
            self.action = 'I'
          elif ((self.error_number == ERROR_AVOID_RIGHT) or (self.error_number == ERROR_BLOCKED_RIGHT)):
            message = 'Object in Way, Failed to go Right -> Avoiding Left.'
            self.action = 'J'
          else:
            message = 'Home Too Small -> Moving Forward.'
            self.action = 'F'
      #2 ..and have reached the zone...
      else:  
        message = 'At Home -> Parking.'
        self.action = 'F'
        self.returned = True
    #1 Home is not in view...
    except ValueError:
        message = 'Cannot See Home -> Searching Left For Home.'
        self.action = 'N'
    print('[Finding Home]...' + message)

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
    elif (self.error_number == ERROR_LOAD):
      self.error = 'LOAD FAILED'
      self.gathered -= 1
    elif (self.error_number == ERROR_PARSE):
      self.error = 'PARSE FAILED'
    elif (self.error_number == ERROR_ACTION):
      self.error = 'BAD ACTION'
    elif (self.error_number == ERROR_BLOCKED_RIGHT):
      self.error = 'BLOCKED AFTER RIGHT TURN'
    elif (self.error_number == ERROR_BLOCKED_LEFT):
      self.error = 'BLOCKED AFTER LEFT TURN'
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
      if (green.command == 'DISCONNECT'):
        green.send_response()
        green.disconnect()
      else:
        green.send_response()
