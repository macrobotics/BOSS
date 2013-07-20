#!/usr/bin/python
import serial
import time

BAUD = 9600
DEVICE = '/dev/ttyS0'

print('[Connecting to Arduino]...')
arduino = serial.Serial(DEVICE,BAUD)

while True:
  action = raw_input('ACTION: ')
  send_time = time.time()
  arduino.write(action)
  print('ERROR: ' + arduino.readline())
  receive_time = time.time()
  print('TIME TO EXECUTE:' + str(receive_time - send_time))
