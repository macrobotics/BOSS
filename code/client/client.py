## client.py
from socket import *

## Constants
# SOCK_STREAM
HOST = 'localhost' # Eventually should be '10.42.0.1' i.e. 'Master'
PORT = 29876 # arbitary port from server.py
ADDR = (HOST,PORT)
BUFSIZE = 4096

## Listen
cli = socket(AF_INET,SOCK_STREAM)
cli.connect((ADDR))
 
data = cli.recv(BUFSIZE)
print data
 
cli.close()
