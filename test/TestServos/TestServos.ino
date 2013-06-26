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
  Serial.println(leftServo.read());
  leftServo.writeMicroseconds(1000);
  leftServo.write(100);
}
