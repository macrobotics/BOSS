#!/usr/bin/python
### Name: Test AutoTill
### Author: Trevor Stanhope
### Organization: Bioresource Engineering, McGill University
### Date: 2013-06-10
### Summary: Automatic field tiller correction using USB camera.
### Requires: Python 2.x

### Imports
import numpy # image processing
from PIL import Image # image processing
from cv2 import * # image capture
from itertools import cycle # circular lists
import time
import subprocess

### Declarations
RATE = 60 # 5 volt per 4096 Hz
CAMERA_INDEX = 0
WIDTH = 640
HEIGHT = 480
CENTER = WIDTH/2
AVERAGES = 4 # number of previous images to store for average
SLOPE = 2.0
MINIMUM = 0.01

### Setup
camera = VideoCapture(CAMERA_INDEX)
camera.set(3,WIDTH)
camera.set(4,HEIGHT)
maxima = [CENTER] * AVERAGES # list of maximas

### Runtime
try:
    ## Operation Loop
    for i in cycle(range(0,AVERAGES)):
        print('------------------')
        (success, frame) = camera.read() # capture image as array
        if success: # if frame captured without errors
            print('SUCCESS')
            raw = Image.fromarray(frame)
            rgb = raw.split()
            red = rgb[0].getdata()
            green = rgb[1].getdata()
            blue = rgb[2].getdata()
            columns = [0] * WIDTH
            
            # Sum columns of image up
            z = 0
            for y in xrange(0,HEIGHT):
                for x in xrange(0,WIDTH):
                    denominator = float(red[z] + blue[z])
                    if denominator == 0:
                        denominator = MINIMUM # don't divide by zero
                    numerator = float(2*green[z])
                    columns[x] += numerator / denominator
                    z += 1 # index in sequence
            
            # Add current maxima to set
            current_maxima = columns.index(numpy.max(columns))
            for y in xrange(0,HEIGHT):
                raw.putpixel((current_maxima,y), (254,254,254))

            # Display Image and Information
            print('Real Maxima: ' + str(current_maxima))
            raw.save("RAW.jpg", "JPEG")
            p = subprocess.Popen(["display", "RAW.jpg"])
            time.sleep(1) # delays for 1 second
            p.kill()
            
        else:
            print('FAILURE')

except KeyboardInterrupt:
    pass
    
