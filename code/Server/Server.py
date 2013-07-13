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
GREEN_RECEIVE = ('10.42.0.3', 50001)
RED_SEND = ('', 60000)
RED_RECEIVE = ('localhost', 60001)
BLUE_SEND = ('', 70000)
BLUE_RECEIVE = ('localhost', 70001)
BUFFER_SIZE = 4096
QUEUE_MAX = 5

class Server:
  def run(self, widget, checkbox, window):
    if (checkbox.get_active()):
      self.send_command('START')
      self.update_gui()
      self.receive_response()
      self.update_gui()
      while (checkbox.get_active()):
        self.send_command('CONTINUE')
        self.update_gui()
        self.receive_response()
        self.update_gui()
      else:
        self.send_command('PAUSE')
        self.update_gui()
        self.receive_response()
        self.update_gui()
    else:
      self.send_command('STOP')
      self.update_gui()
      self.receive_response()
      self.update_gui()
  
  def receive_response(self):
    try:
      print("Receiving ACTION from Green Worker...")
      json_response = self.green_socket_in.recv(BUFFER_SIZE)
      parsed_response = json.loads(json_response)
      action = parsed_response['ACTION']
      error = parsed_response['ERROR']
      gathered = parsed_response['GATHERED']
      self.action_green.set_text(action)
      self.error_green.set_text(error)
      self.gathered_green.set_text(gathered)
      print(str(json_response))
      print("...Success.")
    except socket.error as Error:
      print('...Socket Failure.')
    except ValueError:
      print('...JSON Failure.')

  def send_command(self, command):
    try:
      print("Sending COMMAND to Green Worker...")
      json_command = json.dumps({'COMMAND':command})
      self.green_connection.send(json_command)
      self.command_green.set_text(command)
      print(str(json_command))
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
        print("Establishing SEND port to Green Worker...")
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

  def update_gui(self):
    while gtk.events_pending():
      gtk.main_iteration_do(False)

  def __init__(self): 
    ### Window
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title("BOSS")
    self.window.set_size_request(640, 300)
    self.window.connect("delete_event", self.close)
    self.window.set_border_width(10) 
    ### Table
    self.vbox_app = gtk.VBox(False, 0)
    self.window.add(self.vbox_app)
    self.vbox_app.show()
    self.label_app = gtk.Label("Task Progress: ")
    self.label_app.show()
    self.vbox_app.pack_start(self.label_app, False, False, 6)
    self.table_layout = gtk.Table(rows=4, columns=6, homogeneous=True)
    ### Labels
    self.label_name = gtk.Label("NAME")
    self.label_name.show()
    self.table_layout.attach(self.label_name, 0, 1, 0, 1, 0,0,0,0)
    self.label_status = gtk.Label("STATUS")
    self.label_status.show()
    self.table_layout.attach(self.label_status, 1, 2, 0, 1, 0,0,0,0)
    self.label_command = gtk.Label("COMMAND")
    self.label_command.show()
    self.table_layout.attach(self.label_command, 2, 3, 0, 1, 0,0,0,0)
    self.label_action = gtk.Label("ACTION")
    self.label_action.show()
    self.table_layout.attach(self.label_action, 3, 4, 0, 1, 0,0,0,0)
    self.label_error = gtk.Label("ERROR")
    self.label_error.show()
    self.table_layout.attach(self.label_error, 4, 5, 0, 1, 0,0,0,0)
    self.label_error = gtk.Label("GATHERED")
    self.label_error.show()
    self.table_layout.attach(self.label_error, 5, 6, 0, 1, 0,0,0,0)
    ### Red
    self.label_red = gtk.Label("RED")
    self.label_red.show()
    self.table_layout.attach(self.label_red, 0, 1, 1, 2, 0,0,0,0)
    self.status_red = gtk.Label("DISCONNECTED")
    self.status_red.show()
    self.table_layout.attach(self.status_red, 1, 2, 1, 2, 0,0,0,0)
    self.action_red = gtk.Label("NONE")
    self.action_red.show()
    self.table_layout.attach(self.action_red, 3, 4, 1, 2, 0,0,0,0)
    self.command_red = gtk.Label("STANDBY")
    self.command_red.show()
    self.table_layout.attach(self.command_red, 2, 3, 1, 2, 0,0,0,0)
    self.error_red = gtk.Label("NONE")
    self.error_red.show()
    self.table_layout.attach(self.error_red, 4, 5, 1, 2, 0,0,0,0)
    self.gathered_red = gtk.Label("0")
    self.gathered_red.show()
    self.table_layout.attach(self.gathered_red, 5, 6, 1, 2, 0,0,0,0)
    ### Green
    self.label_green = gtk.Label("GREEN")
    self.label_green.show()
    self.table_layout.attach(self.label_green, 0, 1, 2, 3, 0,0,0,0)
    self.status_green = gtk.Label("DISCONNECTED")
    self.status_green.show()
    self.table_layout.attach(self.status_green, 1, 2, 2, 3, 0,0,0,0)
    self.action_green = gtk.Label("NONE")
    self.action_green.show()
    self.table_layout.attach(self.action_green, 3, 4, 2, 3, 0,0,0,0)
    self.command_green = gtk.Label("STANDBY")
    self.command_green.show()
    self.table_layout.attach(self.command_green, 2, 3, 2, 3, 0,0,0,0)
    self.error_green = gtk.Label("NONE")
    self.error_green.show()
    self.table_layout.attach(self.error_green, 4, 5, 2, 3, 0,0,0,0)
    self.gathered_green = gtk.Label("0")
    self.gathered_green.show()
    self.table_layout.attach(self.gathered_green, 5, 6, 2, 3, 0,0,0,0)
    ### Blue
    self.label_blue = gtk.Label("BLUE")
    self.label_blue.show()
    self.table_layout.attach(self.label_blue, 0, 1, 3, 4, 0,0,0,0)
    self.status_blue = gtk.Label("DISCONNECTED")
    self.status_blue.show()
    self.table_layout.attach(self.status_blue, 1, 2, 3, 4, 0,0,0,0)
    self.action_blue = gtk.Label("NONE")
    self.action_blue.show()
    self.table_layout.attach(self.action_blue, 3, 4, 3, 4, 0,0,0,0)
    self.command_blue = gtk.Label("STANDBY")
    self.command_blue.show()
    self.table_layout.attach(self.command_blue, 2, 3, 3, 4, 0,0,0,0)
    self.error_blue = gtk.Label("NONE")
    self.error_blue.show()
    self.table_layout.attach(self.error_blue, 4, 5, 3, 4, 0,0,0,0)
    self.gathered_blue = gtk.Label("0")
    self.gathered_blue.show()
    self.table_layout.attach(self.gathered_blue, 5, 6, 3, 4, 0,0,0,0)
    ### Total
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
  GUI = Server()
  main()
