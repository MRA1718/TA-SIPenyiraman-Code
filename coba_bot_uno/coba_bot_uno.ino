#include <SoftwareSerial.h>
SoftwareSerial mySerial(2,3);
String data;
char c;
const int RELAY_PIN = 8;

void setup() {
  Serial.begin(115200);
  mySerial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
 }

void loop() {
  while(mySerial.available()>0){
    delay(10);
    c = mySerial.read();
    data += c;
  }   
  if (data.length()>0) {
    Serial.println(data);
    if (data == "RELAY START") {
      digitalWrite(RELAY_PIN, HIGH);
      mySerial.print("RELAY ON");
      delay(180000);
      digitalWrite(RELAY_PIN, LOW);
      mySerial.print("RELAY OFF");
    }
    data = "";
  }
}
