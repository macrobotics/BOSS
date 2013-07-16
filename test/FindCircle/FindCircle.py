import cv2, cv
import numpy as np
import sys

# Setup
BAUD = 9600
DEVICE = '/dev/ttyACM0'
CAMERA_INDEX = 1
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
DP = 4
MIN_DISTANCE = 640
EDGE_THRESHOLD = 150
CENTER_THRESHOLD = 125
MIN_RADIUS = 40
MAX_RADIUS = 60

# Capture
camera = cv2.VideoCapture(CAMERA_INDEX)
camera.set(3,CAMERA_WIDTH)
camera.set(4,CAMERA_HEIGHT)
(success, frame) = camera.read()
if success:
  grayscale = cv2.cvtColor(frame, cv.CV_BGR2GRAY)
  blurred = cv2.GaussianBlur(grayscale, (0,0), 1)
  colored = cv2.cvtColor(blurred,cv2.COLOR_GRAY2BGR)
  (flag, thresholded) = cv2.threshold(blurred, 100, 250, cv2.THRESH_BINARY)
circles = cv2.HoughCircles(thresholded,cv2.cv.CV_HOUGH_GRADIENT,DP,MIN_DISTANCE,param1=EDGE_THRESHOLD, param2=CENTER_THRESHOLD, minRadius=MIN_RADIUS,maxRadius=MAX_RADIUS)

# Display
try:
  circles = np.uint16(np.around(circles))
  for target in circles[0,:]:
    print(target)
    x = target[0]
    y = target[1]
    r = target[2]
    cv2.circle(colored,(x,y),r,(255,0,0),1)
    cv2.circle(colored,(x,y),2,(0,0,255),3)
    cv2.imshow('Detected', colored)
    cv2.imshow('Threshold', thresholded)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
except AttributeError:
  cv2.imshow('Threshold', thresholded)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  print('None detected')

