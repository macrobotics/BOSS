/*
  TestStepperMotor.ino
  Tests the stepper motor loading arm.
  Motor 1 uses: PWM3 and PWM11
  Motor 2 uses: PWM5 and PWM6
  Both use: D4, D7, D8 and D12
*/

/* --- Headers --- */
#include <AFMotor.h>
#define STEPPER_MOTOR 2
#define STEPPER_STEPS 48
#define STEPPER_RPM 10
#define BAUD 9600
#define STEPPER_MOTION 100
#define TIME_LOAD 1000

/* --- Declarations --- */
AF_Stepper stepper(STEPPER_STEPS, STEPPER_MOTOR);
     
void setup() {
  Serial.begin(BAUD);
  stepper.setSpeed(STEPPER_RPM);
}
     
void loop() {
  stepper.step(STEPPER_MOTION, FORWARD, DOUBLE);
  delay(TIME_LOAD);
  stepper.step(STEPPER_MOTION, BACKWARD, DOUBLE);
}
