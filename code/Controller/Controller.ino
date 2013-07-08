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
#define FORWARD 'FORWARD'
#define BACKWARD 'BACKWARD'
#define LEFT 'LEFT'
#define RIGHT 'RIGHT'
#define GRAB 'GRAB'
#define STACK 'STACK'
#define WAIT 'WAIT'

/* --- Declarations right_servo--- */
char command;
int response;
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
  switch(command) {
    case FORWARD:
      response = forward();
    case BACKWARD:
      response = backward();
    case LEFT:
      response = left();
    case RIGHT:
      response = right();
    case GRAB:
      response = grab();
    case STACK:
      response = stack();
    case WAIT:
      response = wait();
    default:
      response = 0;
  }
  Serial.flush();
  Serial.println(response);
}

/* --- Forward --- */
// Move forward
int forward() {
  delay(500);
  return 1;
}

/* --- Backward --- */
// Reverse backward
int backward() {
  delay(500);
  return 1;
}

/* --- Left --- */
// Turn to the left
int left() {
  delay(500);
  return 1;
}
/* --- Right --- */
// Turn to the right
int right() {
  delay(500);
  return 1;
}
/* --- Grab --- */
// Grab bale
int grab() {
  delay(500);
  return 1;
}
/* --- Stack --- */
// Turn 180 and stack objects
int stack() {
  delay(500);
  return 1;
}

/* --- Wait --- */
int wait() {
  delay(1000);
  return 1;
}
