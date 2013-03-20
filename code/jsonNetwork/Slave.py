### Slave.py
### Author: Trevor Stanhope
### Last Update: 2013-03-19

## Imports
from socket import *
import json

## Constants
HOST = 'localhost' # Eventually should be '10.42.0.1' i.e. 'Master'
PORT = 30000 # server port
ADDR = (HOST,PORT)
BUFSIZE = 4096

## Wait for Start
wait = True
while (wait == True):
    tmp = socket(AF_INET,SOCK_STREAM) # tmp socket
    tmp.connect((ADDR))
    msg = tmp.recv(BUFSIZE) # get message as string
    jmsg = json.loads(msg) # re-encode message as json
    HEADER = jmsg["HEADER"] # parse header
    PAYLOAD = jmsg["PAYLOAD"] # parse payload
    print HEADER
    print PAYLOAD
    tmp.close()
