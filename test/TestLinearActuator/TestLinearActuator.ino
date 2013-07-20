/*
  TestLinearActuator
  
  Wiring Diagram:
  blue = Position (0 - 255)
  purple = Position Feedback
  red = 12V
  black = Ground
*/

/* --- Headers --- */
#define ACTUATOR1_PWM_PIN 5
#define ACTUATOR2_PWM_PIN 6
#define ACTUATOR1_POSITION_PIN A4
#define ACTUATOR2_POSITION_PIN A5
#define ACTUATOR_MAX 220
#define ACTUATOR_MIN 0
#define BAUD 9600

/* --- Declarations ---*/
int sensor1 = 0;
int sensor2 = 0;

void setup() {
  Serial.begin(BAUD); 
}

void loop() {
  
  // Get position value.
  sensor1 = analogRead(ACTUATOR1_POSITION_PIN);
  sensor2 = analogRead(ACTUATOR2_POSITION_PIN);  
  
  for (int output = 0; output < 220; output++) {
    
    // Change the analog out value.
    analogWrite(ACTUATOR1_PWM_PIN, output);           
    analogWrite(ACTUATOR2_PWM_PIN, output);           
  
    // Print results.
    Serial.print("sensor1 = " );                       
    Serial.print(sensor1);      
    Serial.print("\t sensor2 = " );                       
    Serial.print(sensor2);      
    Serial.print("\t output = ");      
    Serial.println(output);   
    
    // Delay.
    delay(200);
  }
  
  delay(1000);
  
  for (int output = 220; output > 0; output--) {
    
    // Change the analog out value.
    analogWrite(ACTUATOR1_PWM_PIN, output);           
    analogWrite(ACTUATOR2_PWM_PIN, output);           
  
    // Print results.
    Serial.print("sensor1 = " );                       
    Serial.print(sensor1);      
    Serial.print("\t sensor2 = " );                       
    Serial.print(sensor2);      
    Serial.print("\t output = ");      
    Serial.println(output);   
    
    // Delay.
    delay(200);
  }  
}
