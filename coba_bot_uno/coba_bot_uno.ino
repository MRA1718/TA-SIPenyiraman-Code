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
  int res;
  if(dTanah == 1){
    digitalWrite(power_sTanah, HIGH);
    delay(5000);
    res = analogRead(sTanah1_pin);
    digitalWrite(power_sTanah, LOW);
    return res;
  } else
  if(dTanah == 2){
    digitalWrite(power_sTanah, HIGH);
    delay(5000);
    res = analogRead(sTanah2_pin);
    digitalWrite(power_sTanah, LOW);
    return res;
  }
}

void setup() {
  Serial.begin(115200);
  mySerial.begin(115200);
  pinMode(relay_pin, OUTPUT);
  pinMode(power_sTanah, OUTPUT);
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
      String rep;
      //digitalWrite(power_sTanah, HIGH);
      dsTanah1 = sTanah(1); 
      dsTanah2 = sTanah(2);
      //digitalWrite(power_sTanah, LOW);
      rep = (String) "sensor tanah 1: " + dsTanah1 + ", sensor tanah 2: " + dsTanah2;
      mySerial.print(rep);
    }
    data = "";
  }
}
