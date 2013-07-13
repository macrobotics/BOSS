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
  for (int i = 180; i < 200; i++) {
    right_servo.write(i);
    left_servo.write(i);
    delay(1000);
    Serial.println(i);
  }
}
