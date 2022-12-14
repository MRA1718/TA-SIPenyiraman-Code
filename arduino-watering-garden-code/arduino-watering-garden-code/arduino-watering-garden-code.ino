#include <DFRobot_DHT20.h>

DFRobot_DHT20 dht20;
String data;
char c;
const int power = 13;
const int senSoilPin1 = A0;
const int senSoilPin2 = A1;
const int senLightPin = A2;

//Sensor Tanah
int senSoil(int dSoil) {
  int rSoil;

  if(dSoil == 1) {
    rSoil = analogRead(senSoilPin1);
    return rSoil;
  } else
  if(dSoil == 2) {
    rSoil = analogRead(senSoilPin2);
    return rSoil;
  }
}
//Sensor Cahaya
int senLight() {
  int rLight;

  rLight = analogRead(senLightPin);
  return rLight;
}
//Sensor Suhu & Kelembaban
float senTempt(int dTempt) {
  float rTempt;
  
  if(dTempt == 1) {
    rTempt = dht20.getTemperature();
    return rTempt;
  } else
  if(dTempt == 2) {
    rTempt = dht20.getHumidity()*100;
    return rTempt;
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(power, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0) {
    data = Serial.readStringUntil('\n');
  }
  if(data == "collectData") {
    digitalWrite(power, HIGH);
    delay(500);

    //fetch data Soil Sensor

    //fetch data Light Sensor

    //fetch data Temperature Sensor
    if(!dht20.begin()){
      
    }
    
  }
}
