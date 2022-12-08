const int dPin = 13;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(dPin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(dPin, HIGH);
  delay(10000);
  digitalWrite(dPin, LOW);

  exit(0);
}
