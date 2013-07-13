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
  4: Bad Action
*/

/* --- Headers --- */
#include "SoftwareSerial.h"
#include "stdio.h"
#include "Servo.h"
#define RIGHT_SERVO_PIN 10
#define LEFT_SERVO_PIN 9
#define LOAD_SERVO_PIN 4 
#define ACTUATOR1_PWM_PIN 7 // Blue wire
#define ACTUATOR2_PWM_PIN 8 // Blue wire
#define ACTUATOR1_POSITION_PIN A0 // Purple wire
#define ACTUATOR2_POSITION_PIN A1 // Purple wire
#define ULTRASONIC_PIN 1
#define FORWARD 'FORWARD'
#define BACKWARD 'BACKWARD'
#define LEFT1 'LEFT1'
#define LEFT2 'LEFT2'
#define LEFT3 'LEFT3'
#define RIGHT1 'RIGHT1'
#define RIGHT2 'RIGHT2'
#define RIGHT3 'RIGHT3'
#define GRAB 'GRAB'
#define STACK 'STACK'
#define WAIT 'WAIT'
#define BAUD 9600
#define RANGE_GRAB 10
#define RANGE_MOVE 25
#define TIME_WAIT 250
#define TIME_TURN1 500
#define TIME_TURN2 1000
#define TIME_TURN3 1500
#define TIME_STACK 3000
#define TIME_REVERSE 3000
#define TIME_FORWARD 3000
#define TIME_LOAD 5000
#define TIME_BACKWARD 3000
#define ACTUATOR_MAX 250
#define ACTUATOR_MIN 0
#define CR_SERVO_CCW 0
#define CR_SERVO_CW 200
#define CR_SERVO_STOP 100
#define S_SERVO_MIN 0
#define S_SERVO_MAX 180
#define ERROR_NONE 0
#define ERROR_CLOSE 1
#define ERROR_FAR 2
#define ERROR_LOAD 3
#define ERROR_ACTION 4

/* --- Declarations --- */
char action;
int error;
Servo left_servo;
Servo right_servo;
Servo load_servo;

/* --- Setup --- */
void setup() {
  left_servo.attach(LEFT_SERVO_PIN);
  right_servo.attach(RIGHT_SERVO_PIN);
  load_servo.attach(LOAD_SERVO_PIN);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  action = Serial.read();
  delay(TIME_WAIT);
  switch(action) {
    case FORWARD:
      error = forward();
    case BACKWARD:
      error = backward();
    case LEFT1:
      error = left(TIME_TURN1);
    case LEFT2:
      error = left(TIME_TURN2);
    case LEFT3:
      error = left(TIME_TURN3);
    case RIGHT1:
      error = right(TIME_TURN1);
    case RIGHT2:
      error = right(TIME_TURN2);
    case RIGHT3:
      error = right(TIME_TURN3);
    case GRAB:
      error = grab();
    case STACK:
      error = stack();
    case WAIT:
      error = wait();
    default:
      error = ERROR_ACTION;
  }
  Serial.flush();
  delay(TIME_WAIT);
  Serial.println(error);
}

/* --- Forward --- */
// Move forward
int forward() {
  if (ping() > RANGE_MOVE) {
    right_servo.write(CR_SERVO_CW);
    left_servo.write(CR_SERVO_CCW);
    delay(TIME_FORWARD);
    right_servo.write(CR_SERVO_STOP);
    left_servo.write(CR_SERVO_STOP);    
    return ERROR_NONE;
  }
  else {
    return ERROR_CLOSE; // Object Too Close
  }
}

/* --- Backward --- */
// Reverse backward
int backward() {
  right_servo.write(CR_SERVO_CCW);
  left_servo.write(CR_SERVO_CW);
  delay(TIME_BACKWARD);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  return ERROR_NONE;
}

/* --- Left --- */
// Turn to the left
int left(int duration) {
  right_servo.write(CR_SERVO_CW);
  left_servo.write(CR_SERVO_CW);
  delay(duration);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  if (ping() < RANGE_MOVE) {
    return ERROR_CLOSE;
  }
  else {
    return ERROR_NONE;
  }
}

/* --- Right --- */
// Turn to the right
int right(int duration) {
  right_servo.write(CR_SERVO_CCW);
  left_servo.write(CR_SERVO_CCW);
  delay(duration);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  if (ping() < RANGE_MOVE) {
    return ERROR_CLOSE;
  }
  else {
    return ERROR_NONE;
  }
}

/* --- Grab --- */
// Grab bale
int grab() {
  if (ping() < RANGE_GRAB) {
    load_servo.write(S_SERVO_MAX); // Load bale with servo.
    delay(TIME_LOAD);
    load_servo.write(S_SERVO_MIN); // Reset arm position.
    if (ping() < RANGE_GRAB) {
      return ERROR_LOAD;
    }
    else {
      load_servo.write(S_SERVO_MIN);; // Dejectedly reset arm position.
      return ERROR_NONE; // Load Failed
    }
  }
  else {
    return ERROR_FAR; // Object Too Far
  }
}
/* --- Stack --- */
// Turn 180 and stack objects
int stack() {
  // Turn around
  right_servo.write(CR_SERVO_CW);
  left_servo.write(CR_SERVO_CW);
  delay(TIME_REVERSE);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  
  // Raise rack
  analogWrite(ACTUATOR1_PWM_PIN, ACTUATOR_MAX);
  analogWrite(ACTUATOR2_PWM_PIN, ACTUATOR_MAX);             
  delay(TIME_STACK);
  
  // Move forward
  right_servo.write(CR_SERVO_CW);
  left_servo.write(CR_SERVO_CCW);
  delay(TIME_FORWARD);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  
  // Lower rack
  analogWrite(ACTUATOR1_PWM_PIN, ACTUATOR_MIN);
  analogWrite(ACTUATOR2_PWM_PIN, ACTUATOR_MIN);
  delay(TIME_STACK); 
  return ERROR_NONE;
}

/* --- Wait --- */
int wait() {
  delay(TIME_WAIT);
  return ERROR_NONE;
}

/* --- Ping --- */
// Ping for distance to closest object
long ping() {
  long centimeters;
  pinMode(ULTRASONIC_PIN, OUTPUT);
  digitalWrite(ULTRASONIC_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(ULTRASONIC_PIN, LOW);
  pinMode(ULTRASONIC_PIN, INPUT);
  centimeters = pulseIn(ULTRASONIC_PIN, HIGH) / 29 / 2;
  return centimeters;
}
