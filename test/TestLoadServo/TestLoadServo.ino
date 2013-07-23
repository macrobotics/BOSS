#define BAUD 9600
#define LOAD_SERVO_PIN 11
#define TIME_DEGREE 15
#include "Servo.h"
#define S_SERVO_RESET 0
#define S_SERVO_LOAD 180
#define S_SERVO_CENTER 90

Servo load_servo;

void setup() {
  Serial.begin(BAUD);
  load_servo.attach(LOAD_SERVO_PIN);
}

void loop() {
  use_arm();
}

void use_arm() {
  int last;
  for (int degree = S_SERVO_RESET; degree < S_SERVO_LOAD; degree++) {
    last = load_servo.read();
    load_servo.write(degree);
    delay(TIME_DEGREE);
  }
}

