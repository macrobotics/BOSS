/*
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
Servo left_servo;
Servo right_servo;

/* --- Setup --- */
void setup() {
  left_servo.attach(9);
  right_servo.attach(10);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  left_servo.write(90);
  right_servo.write(90);
  delay(1000);
  left_servo.write(0);
  right_servo.write(0);
  delay(1000);
  left_servo.write(180);
  right_servo.write(180);
  delay(1000);
}
