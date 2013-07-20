/*
  Analog input, analog output, serial output
 
 Reads an analog input pin, maps the result to a range from 0 to 255
 and uses the result to set the pulsewidth modulation (PWM) of an output pin.
 Also prints the results to the serial monitor.
 
 The circuit:
 * potentiometer connected to analog pin 0.
   Center pin of the potentiometer goes to the analog pin.
   side pins of the potentiometer go to +5V and ground
 * LED connected from digital pin 9 to ground
 
 created 29 Dec. 2008
 modified 9 Apr 2012
 by Tom Igoe
 
 This example code is in the public domain.
 
 wiring diagram
 blue = PWM
 purple = position feed back
 red = 12V power
 black = Ground
 
 */

// These constants won't change.  They're used to give names
// to the pins used:
const int analogInPin1 = A4;  // Analog input pin that the potentiometer is attached to
const int analogOutPin1 = 5; // Analog output pin that the LED is attached to
const int analogInPin2 = A5;  // Analog input pin that the potentiometer is attached to
const int analogOutPin2 = 6;

int sensorValue1 = 0;        // value read from the pot
int sensorValue2 = 0;
int outputValue = 0;        // value output to the PWM (analog out)

void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(9600); 
}

void loop() {
  // read the analog in value:
  sensorValue1 = analogRead(analogInPin1);
  sensorValue2 = analogRead(analogInPin2);  
  // map it to the range of the analog out:
  outputValue = 255;  
  // change the analog out value:
  analogWrite(analogOutPin1, outputValue);           
  analogWrite(analogOutPin2, outputValue);           

  // print the results to the serial monitor:
  Serial.print("sensor1 = " );                       
  Serial.print(sensorValue1);      
  Serial.print("\t sensor2 = " );                       
  Serial.print(sensorValue2);      
  Serial.print("\t output = ");      
  Serial.println(outputValue);   

  // wait 2 milliseconds before the next loop
  // for the analog-to-digital converter to settle
  // after the last reading:
  delay(200);                     
}
