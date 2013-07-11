/*
  SLAVE.ino
  License: Creative Commons 2013, Trevor Stanhope
  Updated: 2013-06-13
  Summary: 
*/

/*
  ERRORS
  0: No Error
  1: Object Too Close
  2: Object Too Far
  3: Load Failed

/* --- Headers --- */
#include "SoftwareSerial.h"
#include "stdio.h"
#include "Servo.h"
#define RIGHT_SERVO_PIN 10
#define LEFT_SERVO_PIN 9
#define LOAD_SERVO_PIN 8
#define ACTUATOR_PIN 7
#define ULTRASOUND_PIN 1
#define FORWARD 'FORWARD'
#define BACKWARD 'BACKWARD'
#define LEFT 'LEFT'
#define RIGHT 'RIGHT'
#define GRAB 'GRAB'
#define STACK 'STACK'
#define WAIT 'WAIT'
#define BAUD 9600
#define RANGE 10
#define DEGREES 90 
#define INTERVAL 1000

/* --- Declarations --- */
char action;
int error;
Servo left_servo;
Servo right_servo;
Servo load_servo;
Servo actuator; 

/* --- Setup --- */
void setup() {
  left_servo.attach(LEFT_SERVO_PIN);
  right_servo.attach(RIGHT_SERVO_PIN);
  load_servo.attach(LOAD_SERVO_PIN);
  actuator.attach(ACTUATOR_PIN);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  action = Serial.read();
  delay(INTERVAL);
  switch(action) {
    case FORWARD:
      error = forward();
    case BACKWARD:
      error = backward();
    case LEFT:
      error = left();
    case RIGHT:
      error = right();
    case GRAB:
      error = grab();
    case STACK:
      error = stack();
    case WAIT:
      error = wait();
    default:
      error = 0;
  }
  Serial.flush();
  delay(INTERVAL);
  Serial.println(error);
}

/* --- Forward --- */
// Move forward
int forward() {
  if (ping() > RANGE) {
    right_servo.write(DEGREES);
    left_servo.write(-DEGREES);
    return 0;
  }
  else {
    return 1; // Object Too Close
  }
}

/* --- Backward --- */
// Reverse backward
int backward() {
  right_servo.write(-DEGREES);
  left_servo.write(DEGREES);
  return 0;
}

/* --- Left --- */
// Turn to the left
int left() {
  right_servo.write(DEGREES);
  left_servo.write(DEGREES);
  return 0;
}
/* --- Right --- */
// Turn to the right
int right() {
  right_servo.write(-DEGREES);
  left_servo.write(-DEGREES);
  return 0;
}
/* --- Grab --- */
// Grab bale
int grab() {
  if (ping() <= RANGE) {
    load_servo.write(DEGREES);
    if (ping() > RANGE) {
      return 0;
    }
    else {
      return 3; // Load Failed
    }
  }
  else {
    return 2; // Object Too Far
  }
}
/* --- Stack --- */
// Turn 180 and stack objects
int stack() {
  // Turn around
  right_servo.write(DEGREES);
  left_servo.write(DEGREES);
  // Up rack
  actuator.write(DEGREES);
  // Move forward
  right_servo.write(DEGREES);
  left_servo.write(-DEGREES);
  // Down rack
  actuator.write(-DEGREES);
  return 0;
}

/* --- Wait --- */
int wait() {
  delay(INTERVAL);
  return 0;
}

/* --- Ping --- */
// Ping for distance to closest object
long ping() {
  long centimeters;
  pinMode(ULTRASOUND_PIN, OUTPUT);
  digitalWrite(ULTRASOUND_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASOUND_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(ULTRASOUND_PIN, LOW);
  pinMode(ULTRASOUND_PIN, INPUT);
  centimeters = pulseIn(ULTRASOUND_PIN, HIGH) / 29 / 2;
  return centimeters;
}
