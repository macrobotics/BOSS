#!/usr/bin/env python
### Display.py
### Author: Trevor Stanhope
### Updated: 2013-03-20

import pygtk
pygtk.require('2.0')
import gtk

class Display:
    def callback(self, widget, data):
        print "%s was pressed" % data
        
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
