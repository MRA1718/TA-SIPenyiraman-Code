// constants won't change
const int RELAY_PIN = 8;  // the Arduino pin, which connects to the IN pin of relay

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(115200);
  // initialize digital pin as an output.
  pinMode(RELAY_PIN, OUTPUT);
}

char txt = 0;

// the loop function runs over and over again forever
void loop() {
  if (Serial.available() > 0) {
    txt = Serial.read();

    if (txt == '1')  {
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("ON");
    } else if (txt == '0')  {
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("OFF");
    }
  }
}
