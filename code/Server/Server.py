#!/usr/bin/python
# Imports
import pygtk
pygtk.require('2.0')
import gtk
from socket import *
from time import *
import gtk
import socket
import json
import time

## Global
GREEN_SEND = ('', 50000)
GREEN_RECEIVE = ('localhost', 50001)
BUFFER_SIZE = 4096
QUEUE_MAX = 5

class BOSS_Server:
  def run(self, widget, checkbox, window):
    if (checkbox.get_active()):
      self.send_command('START')
      self.receive_response()
      while (checkbox.get_active()):
        self.send_command('CONTINUE')
        self.receive_response()
        while gtk.events_pending():
          gtk.main_iteration_do(False)
      else:
        self.send_command('PAUSE')
        self.receive_response()
    else:
      self.send_command('STOP')
      self.receive_response()
      while gtk.events_pending():
        gtk.main_iteration_do(False)
  
  def receive_response(self):
    try:
      print("Receiving RESPONSE...")
      json_response = self.green_socket_in.recv(BUFFER_SIZE)
      parsed_response = json.loads(json_response)
      response = parsed_response['RESPONSE']
      print("...Success.")
    except socket.error as Error:
      print('...Socket Failure.')
    except ValueError:
      print('...JSON Failure.')

  def send_command(self, command):
    try:
      print("Sending COMMAND...")
      json_command = json.dumps({'COMMAND':command})
      self.green_connection.send(json_command)
      self.action_green.set_text(command)
      print("...Success.")
    except socket.error as Error:
      print('...Socket Failure.')
    except ValueError:
      print('...JSON Failure.')
      
  def close(self, widget, window):
    try:
      print("Stopping GUI...")
      gtk.main_quit()
      print("...Success.")
    except Exception:
      print("...Failure.")

  def disconnect(self, widget):
    try:
      print("Closing all connections...")
      self.send_command('DISCONNECT')
      self.receive_response()
      self.green_socket_in.close()
      self.green_socket_out.close()
      self.green_connection.close()
      self.green_connected_in = False
      self.green_connected_out = False
      print("...Success.")
    except AttributeError:
      print('...Nothing to Disconnect.')
    self.status_red.set_text('DISCONNECTED')
    self.status_green.set_text('DISCONNECTED')
    self.status_blue.set_text('DISCONNECTED')

  def connect(self, widget):
    if (self.green_connected_out == False) and (self.green_connected_in == False):
      try:
        print("Establishing RECEIVE port from Green...")
        self.green_socket_in = socket.socket(AF_INET,SOCK_STREAM)
        self.green_socket_in.connect((GREEN_RECEIVE))
        self.green_connected_in = True
        print("...Success.")
      except socket.error as msg:
        print('...Failure')
        self.green_socket_in.close()
        self.green_connected_in = False
        pass
      try:
        print("Establishing SEND port to Green...")
        self.green_socket_out = socket.socket(AF_INET,SOCK_STREAM)
        self.green_socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.green_socket_out.bind((GREEN_SEND))
        self.green_socket_out.listen(QUEUE_MAX)
        (self.green_connection, self.green_address) = self.green_socket_out.accept()
        self.green_connected_out = True
        print("...Success.")
      except socket.error as msg:
        self.green_socket_out.close()
        self.green_connected_out = False
        passprint('...Failure')
      self.status_green.set_text('CONNECTED')
    else:
      print('ALREADY CONNECTED')

  def __init__(self): 
    ### Window
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title("BOSS")
    self.window.set_size_request(500, 350)
    self.window.connect("delete_event", self.close)
    self.window.set_border_width(10) 
    ### Table
    self.vbox_app = gtk.VBox(False, 0)
    self.window.add(self.vbox_app)
    self.vbox_app.show()
    self.label_app = gtk.Label("Task Progress: ")
    self.label_app.show()
    self.vbox_app.pack_start(self.label_app, False, False, 6)
    self.table_layout = gtk.Table(rows=4, columns=3, homogeneous=True)
    ### Red
    self.label_red = gtk.Label("Red: ")
    self.label_red.show()
    self.table_layout.attach(self.label_red, 0, 1, 0, 1, 0,0,0,0)
    self.status_red = gtk.Label("DISCONNECTED")
    self.status_red.show()
    self.table_layout.attach(self.status_red, 1, 2, 0, 1, 0,0,0,0)
    self.action_red = gtk.Label("STANDBY")
    self.action_red.show()
    self.table_layout.attach(self.action_red, 2, 3, 0, 1, 0,0,0,0)
    ### Green
    self.label_green = gtk.Label("Green: ")
    self.label_green.show()
    self.table_layout.attach(self.label_green, 0, 1, 1, 2, 0,0,0,0)
    self.status_green = gtk.Label("DISCONNECTED")
    self.status_green.show()
    self.table_layout.attach(self.status_green, 1, 2, 1, 2, 0,0,0,0)
    self.action_green = gtk.Label("STANDBY")
    self.action_green.show()
    self.table_layout.attach(self.action_green, 2, 3, 1, 2, 0,0,0,0)
    ### Blue
    self.label_blue = gtk.Label("Blue: ")
    self.label_blue.show()
    self.table_layout.attach(self.label_blue, 0, 1, 2, 3, 0,0,0,0)
    self.status_blue = gtk.Label("DISCONNECTED")
    self.status_blue.show()
    self.table_layout.attach(self.status_blue, 1, 2, 2, 3, 0,0,0,0)
    self.action_blue = gtk.Label("STANDBY")
    self.action_blue.show()
    self.table_layout.attach(self.action_blue, 2, 3, 2, 3, 0,0,0,0)
    ### Total
    self.label_total = gtk.Label("Total: ")
    self.label_total.show()
    self.table_layout.attach(self.label_total, 0, 1, 3, 4, 0,0,0,0)
    self.status_total = gtk.Label("N/A")
    self.status_total.show()
    self.table_layout.attach(self.status_total, 1, 3, 3, 4, 0,0,0,0)
    self.table_layout.show()
    self.vbox_app.add(self.table_layout)
    ### Hbox
    self.hbox = gtk.HBox(False, 0)
    global b_entry_checkbox
    self.check_box = gtk.CheckButton("RUN")
    self.check_box.connect("toggled", self.run, self.check_box, self.window)
    self.check_box.set_active(False)
    self.hbox.pack_start(self.check_box, True, True, 0)
    self.check_box.show()
    self.button_connect = gtk.Button("CONNECT")
    self.button_connect.connect("clicked", self.connect)
    self.hbox.pack_start(self.button_connect, True, True, 0)
    self.button_connect.show()
    self.button_disconnect = gtk.Button("DISCONNECT")
    self.button_disconnect.connect("clicked", self.disconnect)
    self.hbox.pack_start(self.button_disconnect, True, True, 0)
    self.button_disconnect.show()
    ### Display
    self.hbox.show()
    self.vbox_app.add(self.hbox)
    self.window.show()
    ### Status
    self.green_connected_in = False
    self.green_connected_out = False

# Main Function
def main():
  gtk.main()

# Setup Function
if __name__ == "__main__":
  GUI = BOSS_Server()
  main()
