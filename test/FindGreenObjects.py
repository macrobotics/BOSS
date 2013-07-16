#!/usr/bin/python

### Imports
import numpy # image processing
from numpy import *
from PIL import Image # image processing
from cv2 import * # image capture
from itertools import cycle # circular lists
import time
import subprocess

### Declarations
RATE = 60 # 5 volt per 4096 Hz
LEFT_PIN = 24
RIGHT_PIN = 25
CAMERA_INDEX = 0
WIDTH = 640
HEIGHT = 480
CENTER = WIDTH/2
THRESHOLD = 10
RANGE = 80
BIAS = 10.0
MINIMUM = 1.0
MINIMUM_SIZE = 10
MINIMUM_DISTANCE = 10

### Setup
camera = VideoCapture(CAMERA_INDEX)
camera.set(3,WIDTH)
camera.set(4,HEIGHT)

(success, frame) = camera.read() # capture image as array
raw = Image.fromarray(frame)
BGR = raw.split()
B = array(BGR[0].getdata(), dtype=float32)
G = array(BGR[1].getdata(), dtype=float32)
R = array(BGR[2].getdata(), dtype=float32)
NONTARGET = B + R + MINIMUM
TARGET = BIAS*G
NDI = (TARGET)/(NONTARGET) # convert to normalized difference index
RNDI = NDI.reshape(HEIGHT,WIDTH) # rows by columns
columns = RNDI.sum(axis=0)
rows = RNDI.sum(axis=1)

# Determine Objects
x = 0
xsizes = []
xoffsets = []
xstarts = []
xends = []
while (x < WIDTH-1):
  if (columns[x] > (numpy.mean(columns) + numpy.std(columns))):
    start = x
    while (columns[x] > numpy.mean(columns)) and (x < WIDTH-1):
      x += 1
    end = x
    size = (end - start)
    offset = (start + (end - start)/2)
    xsizes.append(size)
    xoffsets.append(offset)
    xstarts.append(start)
    xends.append(end)
  else:
    x += 1

print('CONSOLIDATED')
print('xstarts' + str(xstarts))
print('xends' + str(xends))
# Display Image and Information
for i in xrange(0,(len(xstarts)-1)):
  for x in xrange(xstarts[i],xends[i]):
    for y in xrange(0,HEIGHT):
      raw.putpixel((x,y), (254,254,254))   

### Determine Action
closest = xsizes.index(numpy.max(xsizes))
distance = 160 - numpy.max(xsizes)
direction = xoffsets[closest]
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

# Display
raw.save("RAW.jpg", "JPEG")
p = subprocess.Popen(["display", "RAW.jpg"])
time.sleep(5)
p.kill()

# Log
with open('columns.csv', 'w') as log:
  for item in columns:
    log.write("%s\n" % str(item))
