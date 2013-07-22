import cv2, cv
import numpy as np
import sys

# Setup
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

#DP = 6 
#MIN_DISTANCE = 640
#EDGE_THRESHOLD = 40
#CENTER_THRESHOLD = 20
#MIN_RADIUS = 10
#MAX_RADIUS = 30

DP = 6 
MIN_DISTANCE = 320
EDGE_THRESHOLD = 40 # param1
CENTER_THRESHOLD = 20 # param2
MIN_RADIUS = 10
MAX_RADIUS = 40

# Capture
camera = cv2.VideoCapture(CAMERA_INDEX)
camera.set(3,CAMERA_WIDTH)
camera.set(4,CAMERA_HEIGHT)
(success, frame) = camera.read()
grayscale = cv2.cvtColor(frame, cv.CV_BGR2GRAY)
blurred = cv2.GaussianBlur(grayscale, (0,0), 5) # (0,0), 5
colored = cv2.cvtColor(blurred,cv2.COLOR_GRAY2BGR)
(flag, thresholded) = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY) # 50 and 255 WORKS
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
except AttributeError:
  print('None detected')
cv2.imshow('DETECTED', colored)
cv2.imshow('THRESHOLD', thresholded)
cv2.imwrite('thresh.jpg', thresholded)
cv2.imwrite('colored.jpg',colored)
cv2.waitKey(0)
cv2.destroyAllWindows()
