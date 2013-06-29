### Slave.py
### Author: Trevor Stanhope
### Last Update: 2013-03-19

## Imports
from socket import *
import json

## Constants
HOST_IN = 'localhost' # Eventually should be '10.42.0.1' i.e. 'Master'
HOST_OUT = ''
PORT_IN = 30000 # master port
PORT_OUT = 30001 # slave port
ADDR_IN = (HOST_IN,PORT_IN)
ADDR_OUT = (HOST_OUT,PORT_OUT)
BUFSIZE = 4096

## Bind Socket
socket_out = socket(AF_INET,SOCK_STREAM) # create a new socket object (serv)
socket_out.bind((ADDR_OUT)) # bind socket to address with new tuple
socket_out.listen(5) # maximum number of queued connections

## Wait for Start
while 1:
	# RECEIVE
    socket_in = socket(AF_INET,SOCK_STREAM) # tmp socket
    socket_in.connect((ADDR_IN))
    msg = socket_in.recv(BUFSIZE) # get message as string
    jmsg = json.loads(msg) # re-encode message as json
    HEADER = jmsg["HEADER"] # parse header
    PAYLOAD = jmsg["PAYLOAD"] # parse payload
    print HEADER
    print PAYLOAD
    socket_in.close()
    
    # SEND
    print 'listening...'
    conn,addr = socket_out.accept() # accept the connection
    print '...connected!'
    HEADER = "TYPE"
    PAYLOAD = "DATA"
    msg = json.dumps({'HEADER':HEADER, 'PAYLOAD':PAYLOAD}) # dump to string
    conn.send(msg)
    conn.close()
