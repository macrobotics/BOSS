/*
  TestContinousServos.ino
  Test program for motion control
  
  Actions:
  1. Left
  2. Right
  3. Forward
  4. Backward
*/

/* --- Headers --- */
#include "SoftwareSerial.h"
#include "stdio.h"
#include "Servo.h"
#define BAUD 9600
#define CR_SERVO_STOP 100
#define CR_SERVO_CW 200
#define CR_SERVO_CCW 0
#define TIME_LEFT 1000
#define TIME_RIGHT 1000
#define TIME_FORWARD 1000
#define TIME_BACKWARD 1000
#define TIME_WAIT 1000

/* --- Declarations --- */
Servo left_servo;
Servo right_servo;

/* --- Setup --- */
void setup() {
  left_servo.attach(9);
  right_servo.attach(10);
  left_servo.write(CR_SERVO_STOP);
  right_servo.write(CR_SERVO_STOP);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  // Turn Left
  left_servo.write(CR_SERVO_CW);
  right_servo.write(CR_SERVO_CW);
  delay(TIME_LEFT);
  left_servo.write(CR_SERVO_STOP);
  right_servo.write(CR_SERVO_STOP);  
  
  // Turn Right
  left_servo.write(CR_SERVO_CCW);
  right_servo.write(CR_SERVO_CCW);
  delay(TIME_RIGHT);
  left_servo.write(CR_SERVO_STOP);
  right_servo.write(CR_SERVO_STOP);  
  
  // Move Forward
  left_servo.write(CR_SERVO_CCW);
  right_servo.write(CR_SERVO_CW);
  delay(TIME_FORWARD);
  left_servo.write(CR_SERVO_STOP);
  right_servo.write(CR_SERVO_STOP);
  
  // Move Backward
  left_servo.write(CR_SERVO_CW);
  right_servo.write(CR_SERVO_CCW);
  delay(TIME_BACKWARD);
  left_servo.write(CR_SERVO_STOP);
  right_servo.write(CR_SERVO_STOP);  
}
