#!/usr/bin/env python
### Display.py
### Author: Trevor Stanhope
### Updated: 2013-03-20

import pygtk
pygtk.require('2.0')
import gtk
from socket import *
import json

## Global
HOST_OUT = '' # master is host
HOST_IN = 'localhost' # address of slave
PORT_OUT = 30000 # master port
PORT_IN = 30001 # slave port
ADDR_OUT = (HOST_OUT,PORT_OUT) # ADDR tuple
ADDR_IN = (HOST_IN,PORT_IN) # ADDR tuple
BUFSIZE = 4096 # reasonable size

class Display:
    def callback(self, widget, data):
        print "%s was pressed" % data
        socket_out = socket(AF_INET,SOCK_STREAM) # create a new socket object (serv)
        socket_out.bind((ADDR_OUT)) # bind socket to address with new tuple
        socket_out.listen(5) # maximum number of queued connections
        while data == "START":
            print "listening..." # need method to break loop on STOP
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
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
        
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Master Display")
        self.window.connect("delete_event", self.delete_event)
        self.window.set_border_width(10)
        self.box1 = gtk.HBox(False, 0)
        self.window.add(self.box1)
        self.button1 = gtk.Button("START")
        self.button1.connect("clicked", self.callback, "START")
        self.box1.pack_start(self.button1, True, True, 0)
        self.button1.show()
        self.button2 = gtk.Button("STOP")
        self.button2.connect("clicked", self.callback, "STOP")
        self.box1.pack_start(self.button2, True, True, 0)
        self.button2.show()
        self.button3 = gtk.Button("EXIT")
        self.button3.connect("clicked", self.delete_event, "EXIT")
        self.box1.pack_start(self.button3, True, True, 0)
        self.button3.show()
        self.box1.show()
        self.window.show()

def main():
    gtk.main()

if __name__ == "__main__":
    hello = Display()
    main()
