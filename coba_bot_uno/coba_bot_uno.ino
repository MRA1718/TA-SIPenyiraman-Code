#include <SoftwareSerial.h>
SoftwareSerial mySerial(2,3);
String data;
char c;
const int relay_pin = 8;
const int power_sTanah = 9;
const int sTanah1_pin = A0;
const int sTanah2_pin = A1;
int dsTanah1, dsTanah2;

int sTanah(int dTanah) {
  if(dtanah == 1){
    analogRead(sTanah1_pin);
  } else
  if(dtanah == 2){
    analogRead(sTanah2_pin);
  }
}

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
    if (data == "nyalakan pompa") {
      digitalWrite(relay_pin, HIGH);
      mySerial.print("pompa menyala");
      delay(180000);
      digitalWrite(relay_pin, LOW);
      mySerial.print("pompa mati");
    } else
    if (data == "sensor tanah") {
      digitalWrite(power_sTanah, HIGH);
      dsTanah1 = sTanah(1); 
      dsTanah2 = sTanah(2);
      digitalWrite(power_sTanah, LOW);
      mySerial.print("sensor tanah 1: " + dsTanah1 + ", sensor tanah 2: " + dsTanah2);
    }
    data = "";
  }
}
