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
  5. Blocked
  6. Orbit Failed
*/

/* --- Headers --- */
#include "SoftwareSerial.h"
#include "stdio.h"
#include "Servo.h"
#include <AFMotor.h>
#define RIGHT_SERVO_PIN 10
#define LEFT_SERVO_PIN 9
#define LOAD_SERVO_PIN 11
#define ACTUATOR1_PWM_PIN 5 // Blue wire
#define ACTUATOR2_PWM_PIN 6 // Blue wire
#define ACTUATOR1_POSITION_PIN A4 // Purple wire
#define ACTUATOR2_POSITION_PIN A5 // Purple wire
#define ULTRASONIC_PIN 8
#define BAUD 9600
#define RANGE_GRAB 20 // maximum distance (cm) to grab object
#define RANGE_STUCK 15
#define TIME_WAIT 1000
#define TIME_LEFT 100
#define TIME_RIGHT 100
#define TIME_DUMP 3000
#define TIME_REVERSE 3000
#define TIME_FORWARD 2000
#define TIME_LOAD 5000
#define TIME_BACKWARD 2000
#define TIME_STEP 100
#define TIME_DEGREE 15
#define ACTUATOR_MAX 220
#define ACTUATOR_MIN 0
#define CR_SERVO_CCW 50
#define CR_SERVO_CW 150
#define CR_SERVO_STOP 100
#define S_SERVO_RESET 30
#define S_SERVO_LOAD 180
#define S_SERVO_CENTER 90

/* --- Prototypes --- */
char forward(void);
char backward(void);
char left(int val);
char right(int val);
char grab(void);
char dump(void);
char avoid(void);
char right_orbit(void);
char left_orbit(void);
long ping(void);
char wait(void);
char extend_arm(void);
char use_arm(void);
char center_arm(void);

/* --- Error Codes --- */
const char ERROR_NONE = '0';
const char ERROR_CLOSE = '1';
const char ERROR_FAR = '2';
const char ERROR_LOAD = '3';
const char ERROR_ACTION = '4';
const char ERROR_BLOCKED = '5';
const char ERROR_LEFT_ORBIT = '6';
const char ERROR_RIGHT_ORBIT = '7';
const char ERROR_AVOID = '8';

/* --- Basic Actions --- */
const char MOVE_FORWARD = 'F';
const char MOVE_BACKWARD = 'B';
const char NEAR_LEFT = 'K';
const char LEFT = 'L';
const char FAR_LEFT = 'M';
const char FULL_LEFT = 'N';
const char NEAR_RIGHT = 'Q';
const char RIGHT = 'R';
const char FAR_RIGHT = 'S';
const char FULL_RIGHT = 'T';
const char WAIT = 'W';
const char EXTEND_ARM = 'E';
const char USE_ARM = 'U';
const char CENTER_ARM = 'C';
const char TURN_AROUND = 'Z';

/* --- Complex --- */
const char GRAB = 'G';
const char DUMP = 'D';
const char AVOID = 'A';
const char RIGHT_ORBIT = 'O';
const char LEFT_ORBIT = 'P';

/* --- Declarations ---*/
char action;
char error;
Servo left_servo;
Servo right_servo;
Servo load_servo;

/* --- Setup --- */
void setup() {
  left_servo.attach(LEFT_SERVO_PIN);
  right_servo.attach(RIGHT_SERVO_PIN);
  load_servo.attach(LOAD_SERVO_PIN);
  left_servo.write(CR_SERVO_STOP);
  right_servo.write(CR_SERVO_STOP);
  load_servo.write(S_SERVO_RESET);
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
    case NEAR_LEFT:
      error = left(1);
      break;
    case LEFT:
      error = left(2);
      break;
    case FAR_LEFT:
      error = left(3);
      break;
    case FULL_LEFT:
      error = left(4);
      break;
    case NEAR_RIGHT:
      error = right(1);
      break;
    case RIGHT:
      error = right(2);
      break;
    case FAR_RIGHT:
      error = right(3);
      break;
    case FULL_RIGHT:
      error = right(4);
      break;
    case GRAB:
      error = grab();
      break;
    case DUMP:
      error = dump();
      break;
    case WAIT:
      error = wait();
      break;
    case RIGHT_ORBIT:
      error = right_orbit();
      break;
    case LEFT_ORBIT:
      error = left_orbit();
      break;
    case AVOID:
      error = avoid();
      break;
    case EXTEND_ARM:
      error = extend_arm();
      break;
    case USE_ARM:
      error = use_arm();
      break;
    case CENTER_ARM:
      error = center_arm();
      break;
    case TURN_AROUND:
      error = right(60);
      break;
    default:
      error = ERROR_ACTION;
      break;
  }
  if (error != ERROR_ACTION) {
    Serial.flush();
    delay(TIME_WAIT);
    Serial.println(error);
  }
  else {
    Serial.flush();
  }
}

/* --- Forward --- */
// Attempt to move forward
char forward() {
  
  // Prepare
  char error;
  char temp;
  
  // Try
  if (ping() > RANGE_GRAB) {
    temp = center_arm();
    right_servo.write(CR_SERVO_CW);
    left_servo.write(CR_SERVO_CCW);
    delay(TIME_FORWARD);
    right_servo.write(CR_SERVO_STOP);
    left_servo.write(CR_SERVO_STOP);
    error = ERROR_NONE;  
  }
  else {
    error = ERROR_CLOSE; // Object Too Close
  }
  
  // Finish
  return error;
}

/* --- Backward --- */
// Reverse backward
char backward() {
  
  // Prepare
  char error = ERROR_NONE;
  
  // Reverse
  right_servo.write(CR_SERVO_CCW);
  left_servo.write(CR_SERVO_CW);
  delay(TIME_BACKWARD);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  
  // Return Errors
  return error;
}

/* --- Left --- */
char left(int val) {
  
  // Prepare
  char error;
  
  // Turn Left
  right_servo.write(CR_SERVO_CW);
  left_servo.write(CR_SERVO_CW);
  delay(val*TIME_LEFT);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  
  // Return Errors
  if (ping() < RANGE_GRAB) {
    error = ERROR_BLOCKED;
  }
  else {
    error = ERROR_NONE;
  }
  return error;
}

/* --- Right --- */
char right(int val) {
  
  // Prepare
  char error;
    
  // Turn Right
  right_servo.write(CR_SERVO_CCW);
  left_servo.write(CR_SERVO_CCW);
  delay(val*TIME_RIGHT);
  right_servo.write(CR_SERVO_STOP);
  left_servo.write(CR_SERVO_STOP);
  
  // Return Errors
  if (ping() < RANGE_GRAB) {
    error = ERROR_BLOCKED;
  }
  else {
    error = ERROR_NONE;
  }
  return error;  
}

/* --- Grab --- */
char grab() {
  
  // Prepare
  char error;
  char temp = extend_arm();
  
  // Execute Action
  if (ping() < RANGE_GRAB) {
    while (ping() > RANGE_GRAB) {
      right_servo.write(CR_SERVO_CW);
      left_servo.write(CR_SERVO_CCW);
      delay(TIME_STEP);
    }
    right_servo.write(CR_SERVO_STOP);
    left_servo.write(CR_SERVO_STOP);
    temp = use_arm();
    if (ping() < RANGE_STUCK) {
      error = ERROR_LOAD;
    }
    else {
      error = ERROR_NONE;
    }
  }
  else {
    error = ERROR_FAR;
  }
  
  // Return errors
  temp = extend_arm();
  return error;
}

/* --- Dump --- */
char dump() {
  
  // Prepare
  char error;
  char temp;
  
  // Prepare
  error = right(60);
  
  // Tuck Arm
  error = center_arm();
  
  // Raise rack
  analogWrite(ACTUATOR1_PWM_PIN, ACTUATOR_MAX);
  analogWrite(ACTUATOR2_PWM_PIN, ACTUATOR_MAX);             
  delay(TIME_DUMP);
  
  // Move forward
  error = forward();
  delay(TIME_WAIT);
  
  // Lower rack
  analogWrite(ACTUATOR1_PWM_PIN, ACTUATOR_MIN);
  analogWrite(ACTUATOR2_PWM_PIN, ACTUATOR_MIN);
  delay(TIME_DUMP); 
  
  // Extend arm
  error = extend_arm();
  
  // Return Errors
  return error;
}

/* --- Avoid --- */
char avoid() {
  
  // Prepare
  char error = ERROR_NONE;
  char temp = center_arm();
  
  // Turn right
  error = right(2);
  
  // Move forward
  error = forward();
  
  // Turn Left
  error = left(2);
  
  // Move forward
  error = forward();
  
  // Return error
  return error;
}

/* --- Right Orbit --- */
char right_orbit() {
  
  // Prepare
  char error = ERROR_NONE;
  char temp;
  
  // Turn right
  error = right(15);
  
  // Try to move forward
  switch (error) {
    // if clear move forward
    case ERROR_NONE:
      error = forward();
      switch (error) {
        // if successful turn back
        case ERROR_NONE:
          error = left(30);
          break;
        // if unsuccessful turn back
        case ERROR_CLOSE:
          error = left(15);
          error = ERROR_RIGHT_ORBIT;
          break;
      }
      break;
    // if can't. turn back
    case ERROR_CLOSE:
      error = left(15);
      error = ERROR_RIGHT_ORBIT;
      break;
  }
  // Return Errors
  return error;
}

/* --- Left Orbit --- */
char left_orbit() {
  char error = ERROR_NONE;
  
  // Turn right
  error = left(15);
  
  // Try to move forward
  switch (error) {
    // if clear move forward
    case ERROR_NONE:
      error = forward();
      switch (error) {
        // if successful turn back
        case ERROR_NONE:
          error = right(30);
          break;
        // if unsuccessful turn back
        case ERROR_CLOSE:
          error = right(15);
          error = ERROR_LEFT_ORBIT;
          break;
      }
      break;
    // if can't. turn back
    case ERROR_CLOSE:
      error = left(15);
      error = ERROR_LEFT_ORBIT;
      break;
  }
  // Return Errors
  return error;
}

/* --- Wait --- */
char wait() {
  char error = ERROR_NONE;
  error = center_arm();
  delay(TIME_WAIT);
  return error;
}

/* --- Ping --- */
// Ping for distance to closest object
long ping() {
  int centimeters;
  pinMode(ULTRASONIC_PIN, OUTPUT);
  digitalWrite(ULTRASONIC_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(ULTRASONIC_PIN, LOW);
  pinMode(ULTRASONIC_PIN, INPUT);
  centimeters = pulseIn(ULTRASONIC_PIN, HIGH) / 28 / 2;
  return centimeters;
}

/* --- Helper Functions --- */
char extend_arm() {
  for (int degree = S_SERVO_LOAD; degree > S_SERVO_RESET; degree--) {
    load_servo.write(degree);
    delay(TIME_DEGREE);
  }
  return ERROR_NONE;
}

char use_arm() {
  for (int degree = S_SERVO_RESET; degree < S_SERVO_LOAD; degree++) {
    load_servo.write(degree);
    delay(TIME_DEGREE);
  }
  return ERROR_NONE;
}

char center_arm() {
  int start = load_servo.read();
  if (start > S_SERVO_CENTER) {
    for (int degree = start; degree > S_SERVO_CENTER; degree--) {
      load_servo.write(degree);
      delay(TIME_DEGREE);
    }
  }
  else {
    for (int degree = start; degree < S_SERVO_CENTER; degree++) {
      load_servo.write(degree);
      delay(TIME_DEGREE);
    }
  }
  return ERROR_NONE;
}
