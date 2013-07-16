#!/usr/bin/python
# Worker.py
# MacRobotics

# Imports
from serial import SerialException
from socket import *
from numpy import *
from PIL import Image 
from cv2 import VideoCapture
from cv import CaptureFromCAM, QueryFrame
from time import *
import numpy
import socket
import time
import json
import serial
import sys
import ast
import subprocess

# Setup
ADDRESS_IN = ('localhost',50000)
ADDRESS_OUT = ('localhost',50001)
BUFFER_SIZE = 4096
QUEUE_MAX = 5
BAUD = 9600
DEVICE = '/dev/ttyACM0' # '/dev/ttyS0' for AlaMode, '/dev/ttyAMC0' for Uno
CAMERA_INDEX = 0
WIDTH = 640.0
HEIGHT = 480.0
CENTER = WIDTH/2.0
THRESHOLD = CENTER/4.0
ERROR = pi/32.0
RANGE = WIDTH/1.5
BIAS = 100.0
MINIMUM_COLOR = 0.01
MINIMUM_SIZE = WIDTH/32.0
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

# Class Worker
class Worker:
  ## Initialize Worker robot.
  def __init__(self):
#    try:
#      print('Setting up Camera...')
#      self.camera = VideoCapture(CAMERA_INDEX)
#      self.camera.set(3,WIDTH)
#      self.camera.set(4,HEIGHT)
#      self.camera
#      print('...Success.')
#    except Exception:
#     print('...Failure.')
    try:
      print('Setting up Controller...')
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
      self.error = None
      self.error_number = None
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
    camera = VideoCapture(CAMERA_INDEX)
    camera.set(3,WIDTH)
    camera.set(4,HEIGHT)
    (success, frame) = camera.read()
    camera.release()
    raw = Image.fromarray(frame)
    BGR = raw.split()
    B = array(BGR[0].getdata(), dtype=float32)
    G = array(BGR[1].getdata(), dtype=float32)
    R = array(BGR[2].getdata(), dtype=float32)
    NDI_G = (BIAS*G + MINIMUM)/(R+B+MINIMUM_COLOR)
    green_image = NDI_G.reshape(HEIGHT,WIDTH)
    green_columns = green_image.sum(axis=0)
    green_high = numpy.mean(green_columns) + numpy.std(green_columns)
    green_low = numpy.mean(green_columns)
    x = 0
    self.green_objects = []
    while (x < WIDTH-1):
      if (green_columns[x] > green_high):
        start = x
        while (green_columns[x] > green_low) and (x < WIDTH-1):
          x += 1
        end = x
        size = (end - start)
        offset = (start + (end - start)/2) - CENTER
        if (size > MINIMUM_SIZE):
          self.green_objects.append((size,offset,start,end))
      else:
        x += 1

    # Display
    for (size,offset,start,end) in self.green_objects:
      for x in xrange(start,end):
        for y in xrange(0,HEIGHT):
          raw.putpixel((x,y), (254,254,254))   
    raw.save("RAW.jpg", "JPEG")
    p = subprocess.Popen(["display", "RAW.jpg"])
    time.sleep(5)
    p.kill()

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
  
  ## Receives COMMAND from Server.
  def receive_command(self):
    try: 
      print('Receiving COMMAND from Server...')
      json_command = self.socket_in.recv(BUFFER_SIZE)
      dict_command = json.loads(json_command)
      self.command = dict_command['COMMAND']
      print(str(json_command))
      print('...Success.')
    except socket.error as SocketError:
      print('...Connection Failure.')

  ## After receiving COMMAND, determine action.
  def decide_action(self):
    if (self.command == 'START') or (self.command == 'CONTINUE'):
      if (self.gathered < 4):
        self.gather()
      elif (not self.stacked):
        self.stack()
      elif (not self.returned):
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
      self.action = 'UNKNOWN'
    self.previous_actions.append(self.action)

  ## Gather Logic
  def gather(self):
    self.goal = 'GATHERING'
    self.use_camera()
    (size,offset,start,end) = max(self.green_objects)
    print('Detected Size:' + str(size))
    print('Detected Offset:' + str(offset))
    if (offset > THRESHOLD) and (size > MINIMUM_SIZE):
      self.action = 'R'
      self.orientation += TURN #!
    elif (offset < -THRESHOLD) and (size > MINIMUM_SIZE):
      self.action = 'L'
      self.orientation -= TURN #!
    elif (size > MINIMUM_SIZE):
      if (size > RANGE):
        self.action = 'G'
        self.gathered += 1 #!
      elif (not self.error_number == ERROR_CLOSE):
        self.action = 'F'
        self.x += TRAVEL*cos(self.orientation) #!
        self.y += TRAVEL*sin(self.orientation) #!
      else:
        self.action = 'R'
        self.orientation += TURN #!
    else:
      self.action = 'R'
      self.orientation += TURN #!

  ## Stack Logic
  def stack(self):
    self.goal = 'STACKING'
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
    self.goal = 'RETURNING'
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
      print('Sending ACTION to Controller...')
      print(self.action)
      self.arduino.write(self.action)
      print('...Success.')
    except Exception:
      print('...Failure.')

    ### Receive
    try:
      print('Receiving ERROR from Controller...')
      self.error_number = int(self.arduino.readline())
      print(self.error_number)
      print('...Success.')
    except ValueError:
      self.error_number = ERROR_PARSE
      print("ValueError: Failed to parse signal, retrying...")
    except OSError:
      self.error_number = ERROR_CONNECTION
      print("OSError: Connection lost, retrying...")
    except SerialException:
      self.error_number = ERROR_CONNECTION
      print("Serial Exception: Connection lost, retrying...")
    except SyntaxError:
      self.error_number = ERROR_PARSE
      print("Syntax Error: Failed to parse signal, retrying...")
    except KeyError:
      self.error_number = ERROR_PARSE
      print("KeyError: Failed to parse signal, retrying...")

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

  ## Send RESPONSE to Server
  def send_response(self):   
    try:
      print('Sending RESPONSE to Server ...')
      json_response = json.dumps({'ACTION':self.action, 'ERROR':self.error, 'GATHERED':str(self.gathered), 'GOAL':self.goal})
      self.connection.send(json_response)
      print(str(json_response))
      print("...Success.")
    except Exception:
      print("...Failure.")

  ## Disconnect from Server.
  def disconnect(self):
    try:
      print('Disconnecting from Server...')
      self.socket_in.close()
      self.socket_out.close()
      self.connection.close()
      self.connected_in = False
      self.connected_out = False
      print('...Success')
    except Exception:
      print('...Failure')
      pass

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
