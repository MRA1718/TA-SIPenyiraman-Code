// constants won't change
const int RELAY_PIN = 5;  // the Arduino pin, which connects to the IN pin of relay

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(115200);
  // initialize digital pin as an output.
  pinMode(RELAY_PIN, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(RELAY_PIN, HIGH);
  Serial.println("ON");
  delay(5000);
  digitalWrite(RELAY_PIN, LOW);
  Serial.println("OFF");
  delay(5000);
}
