### Master.py
### Author: Trevor Stanhope
### Last Update: 2013-03-19

## Imports
from socket import *
import json

## Constants
HOST_OUT = '' # master is host
HOST_IN = 'localhost' # address of slave
PORT_OUT = 30000 # master port
PORT_IN = 30001 # slave port
ADDR_OUT = (HOST_OUT,PORT_OUT) # ADDR tuple
ADDR_IN = (HOST_IN,PORT_IN) # ADDR tuple
BUFSIZE = 4096 # reasonable size

## Bind Socket
socket_out = socket(AF_INET,SOCK_STREAM) # create a new socket object (serv)
socket_out.bind((ADDR_OUT)) # bind socket to address with new tuple
socket_out.listen(5) # maximum number of queued connections

while 1:
    # SEND
    print 'listening...'
    conn,addr = socket_out.accept() # accept the connection
    print '...connected!'
    HEADER = "TYPE"
    PAYLOAD = "DATA"
    msg = json.dumps({'HEADER':HEADER, 'PAYLOAD':PAYLOAD}) # dump to string
    conn.send(msg)
    conn.close()
    
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
