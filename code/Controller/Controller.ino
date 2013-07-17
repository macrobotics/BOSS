/*
  Controller.ino
  License: Creative Commons 2013, Trevor Stanhope
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
#include <AFMotor.h>
#define STEPPER_MOTOR 2
#define STEPPER_STEPS 48
#define STEPPER_RPM 10
#define RIGHT_SERVO_PIN 10
#define LEFT_SERVO_PIN 9
#define STEPPER_LOAD 100
#define STEPPER_MOTOR 1 // PWM3, PWM11, D4, D7, D8 and D12
#define ACTUATOR1_PWM_PIN 5 // Blue wire
#define ACTUATOR2_PWM_PIN 6 // Blue wire
#define ACTUATOR1_POSITION_PIN A0 // Purple wire
#define ACTUATOR2_POSITION_PIN A1 // Purple wire
#define ULTRASONIC_PIN 2
#define BAUD 9600
#define RANGE_GRAB 20 // minimum distance (cm) to grab object
#define RANGE_MOVE 40 // minimum distance (cm) to object if moving
#define TIME_WAIT 250
#define TIME_LEFT 500
#define TIME_RIGHT 1000
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
#define S_SERVO_RESET 0
#define S_SERVO_LOAD 180

/* --- Prototypes --- */
char forward(void);
char backward(void);
char left(void);
char right(void);
char grab(void);
char stack(void);
long ping(void);
char wait(void);

/* --- Declarations --- */
const char ERROR_NONE = '0';
const char ERROR_CLOSE = '1';
const char ERROR_FAR = '2';
const char ERROR_LOAD = '3';
const char ERROR_ACTION = '4';
const char MOVE_FORWARD = 'F';
const char MOVE_BACKWARD = 'B';
const char LEFT = 'L';
const char RIGHT = 'R';
const char GRAB = 'G';
const char STACK = 'S';
const char WAIT = 'W';
char action;
char error;
Servo left_servo;
Servo right_servo;
AF_Stepper stepper(STEPPER_STEPS, STEPPER_MOTOR);

/* --- Setup --- */
void setup() {
  left_servo.attach(LEFT_SERVO_PIN);
  right_servo.attach(RIGHT_SERVO_PIN);
  left_servo.write(CR_SERVO_STOP);
  right_servo.write(CR_SERVO_STOP);
  stepper.setSpeed(STEPPER_RPM);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  action = Serial.read();
  switch(action) {
    case MOVE_FORWARD:
      error = forward();
      break;
    case MOVE_BACKWARD:
      error = backward();
      break;
    case LEFT:
      error = left();
      break;
    case RIGHT:
      error = right();
      break;
    case GRAB:
      error = grab();
      break;
    case STACK:
      error = stack();
      break;
    case WAIT:
      error = wait();
      break;
    default:
      error = ERROR_ACTION;
  }
  if (error != ERROR_ACTION) {
    Serial.flush();
    delay(TIME_WAIT);
    Serial.println(0); // Serial.println(error);
  }
  else {
    Serial.flush();
  }
}

/* --- Forward --- */
// Move forward
char forward() {
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
char backward() {
  right_servo.write(CR_SERVO_CCW);
  left_servo.write(CR_SERVO_CW);
  delay(TIME_BACKWARD);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  return ERROR_NONE;
}

/* --- Left --- */
// Turn to the left
char left() {
  right_servo.write(CR_SERVO_CW);
  left_servo.write(CR_SERVO_CW);
  delay(TIME_LEFT);
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
char right() {
  right_servo.write(CR_SERVO_CCW);
  left_servo.write(CR_SERVO_CCW);
  delay(TIME_RIGHT);
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
char grab() {
  if (ping() < RANGE_GRAB) {
    stepper.step(STEPPER_LOAD, FORWARD, DOUBLE);
    delay(TIME_LOAD);
    stepper.step(STEPPER_LOAD, BACKWARD, DOUBLE); // Reset arm position.
    if (ping() < RANGE_GRAB) {
      return ERROR_LOAD;
    }
    else {
      stepper.step(STEPPER_LOAD, BACKWARD, DOUBLE); // Dejectedly reset arm position.
      return ERROR_NONE; // Load Failed
    }
  }
  else {
    return ERROR_FAR; // Object Too Far
  }
}
/* --- Stack --- */
// Turn 180 and stack objects
char stack() {
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
char wait() {
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
