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

/* --- Declarations --- */
char COMMAND;
boolean RESPONSE;
Servo leftServo;
Servo rightServo;

/* --- Setup --- */
void setup() {
  leftServo.attach(9);
  rightServo.attach(10);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  COMMAND = Serial.read();
  delay(1000);
  switch(COMMAND) {
    case '1':
      RESPONSE = forward();
    case '2':
      RESPONSE = backward();
    case 'l':
      RESPONSE = left();
    case 'r':
      RESPONSE = right();
    case 'g':
      RESPONSE = grab();
    case 's':
      RESPONSE = stack();
    default:
      break;
  }
  Serial.flush();
  Serial.println(RESPONSE);
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
