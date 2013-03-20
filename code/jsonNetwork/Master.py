### Master.py
### Author: Trevor Stanhope
### Last Update: 2013-03-19

## Imports
from socket import *
import json

## Constants
HOST_OUT = '' # we are the host
PORT_OUT = 30000
ADDR_OUT = (HOST_OUT,PORT_OUT) # ADDR tuple
BUFSIZE = 4096 # reasonable size

## Bind Socket
serv = socket(AF_INET,SOCK_STREAM) # create a new socket object (serv)
serv.bind((ADDR_OUT)) # bind socket to address with new tuple
serv.listen(5) # maximum number of queued connections

while 1:
    print 'listening...'
    conn,addr = serv.accept() # accept the connection
    print '...connected!'
    HEADER = "TYPE"
    PAYLOAD = "DATA"
    msg = json.dumps({'HEADER':HEADER, 'PAYLOAD':PAYLOAD}) # dump to string
    conn.send(msg)
    conn.close()
