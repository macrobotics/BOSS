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
Servo load_servo;

/* --- Setup --- */
void setup() {
  load_servo.attach(11);
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  int maxima = 180;
  int minima = 10;
  for (int degree = minima; degree < maxima; degree++) {
    load_servo.write(degree);
    delay(15);
  }
  for (int degree = maxima; degree > minima; degree--) {
    load_servo.write(degree);
    delay(15);
  }
}
