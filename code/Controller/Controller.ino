/*
  SLAVE.ino
  License: Creative Commons 2013, Trevor Stanhope
  Updated: 2013-06-13
  Summary: 
*/

/* --- Headers --- */
#include "SoftwareSerial.h"
#include "stdio.h"
#include "Servo.h"
#define BAUD 9600
#define RIGHT_SERVO_PIN 10
#define LEFT_SERVO_PIN 9
#define FORWARD 'F'
#define BACKWARD 'B'
#define LEFT 'L'
#define RIGHT 'R'
#define GRAB 'G'
#define STACK 'S'

/* --- Declarations right_servo--- */
char command;
boolean respose;
Servo left_servo;
Servo right_servo;

/* --- Setup --- */
void setup() {
  left_servo.attach(LEFT_SERVO_PIN);
  right_servo.attach(RIGHT_SERVO_PIN);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  command = Serial.read();
  delay(1000);
  switch(command) {
    case FORWARD:
      respose = forward();
    case BACKWARD:
      respose = backward();
    case LEFT:
      respose = left();
    case RIGHT:
      respose = right();
    case GRAB:
      respose = grab();
    case STACK:
      respose = stack();
    default:
      break;
  }
  Serial.flush();
  Serial.println(respose);
}

/* --- Forward --- */
// Move forward
boolean forward() {
  delay(500);
  return true;
}

/* --- Backward --- */
// Reverse backward
boolean backward() {
  delay(500);
  return true;
}

/* --- Left --- */
// Turn to the left
boolean left() {
  delay(500);
  return true;
}
/* --- Right --- */
// Turn to the right
boolean right() {
  delay(500);
  return true;
}
/* --- Grab --- */
// Grab bale
boolean grab() {
  delay(500);
  return true;
}
/* --- Stack --- */
// Turn 180 and stack objects
boolean stack() {
  delay(500);
  return true;
}
