// findLocation.ino
// Trevor Stanhope, McGill Bioresource Fid
// January 23rd, 2013
// Finds position on grid given known landmarks

/* Headers */
#include "config.h"
#include <Servo.h>
#include <StackArray.h>

/* Global */
Servo moveServo;
Servo turnServo;
StackArray <int> stack;
int locations[8][8] = {0}; // initialize unknown grid

/* Primary Functions */
void setup() {
    stack.push(0); // initiate stack at state-zero
    pinMode(CENTERPIN, OUTPUT);
    moveServo(MOVEPIN);
    turnServo(TURNPIN);
}

void loop() {
    int top = stack.peek();
    if (top == 0) {
        move()
        stack.push(1); // 1 means moved forward
    }
    else if (top == 1) {
        getLine()
    }
}

/* Secondary Functions */

void move(distance) {
    int degrees = 360*distance/WHEELCIRCUMFERENCE;
    moveServo.write(degrees); // dependent on line width
}

void turn(degrees) {
    turnServo.write(degrees);
}

int getDirection() {
    // get direction from compass
}
