const int p_sLight = 13;
const int pin_sLight = A2;
int x = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(p_sLight, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(p_sLight, HIGH);
  delay(1000);
  
  while(x<10) {
    Serial.println(analogRead(pin_sLight));
    x = x + 1;
    delay(1000);
  }

  digitalWrite(p_sLight, LOW);
  delay(1000);
  
  exit(0);
}
