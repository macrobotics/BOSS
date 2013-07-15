#define ULTRASONIC_PIN 3
#define BAUD 9600

/* --- Setup --- */
void setup() {
  Serial.begin(BAUD);
}

/* --- Loop --- */
void loop() {
  Serial.println(ping());
}

/* --- Ping --- */
// Ping for distance to closest object
long ping() {
  long centimeters;
  pinMode(ULTRASONIC_PIN, OUTPUT);
  digitalWrite(ULTRASONIC_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(ULTRASONIC_PIN, LOW);
  pinMode(ULTRASONIC_PIN, INPUT);
  centimeters = pulseIn(ULTRASONIC_PIN, HIGH) / 29 / 2;
  return centimeters;
}
