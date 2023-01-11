#include <ArduinoJson.h>
#include <DFRobot_DHT20.h>


DFRobot_DHT20 dht20;
String data;
const int power = 13;
const int senSoilPin1 = A0;
const int senSoilPin2 = A1;
const int senLightPin = A2;
const int waterMoistVal = 0;
const int airMoistVal = 650;
StaticJsonDocument<64> doc;
int s1, s2, l, t, h, sc1, sc2;

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
int senTempt(int dTempt) {
  int rTempt;
  
  if(dTempt == 1) {
    rTempt = (dht20.getTemperature());
    return rTempt;
  } else
  if(dTempt == 2) {
    rTempt = (dht20.getHumidity()*100);
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
    
    if(data == "collectdata") {
    digitalWrite(power, HIGH);
    delay(500);
    
    //fetch data Soil Sensor
    s1 = senSoil(1);
    s2 = senSoil(2);
    sc1 = map(s1, airMoistVal, waterMoistVal, 0, 100);
    sc2 = map(s2, airMoistVal, waterMoistVal, 0, 100);   
    //fetch data Temperature Sensor
    if(!dht20.begin()){
      t = int(senTempt(1));
      h = int(senTempt(2));
    }
    //fetch data Light Sensor
    l = senLight();

    digitalWrite(power,LOW);

    doc["soil1"] = s1;
    doc["soil2"] = s2;
    doc["soilc1"] = sc1;
    doc["soilc2"] = sc2;
    doc["temp"] = t;
    doc["humidity"] = h;
    doc["light"] = l;

    serializeJson(doc, Serial);
    Serial.println();
    delay(1000);
    } 
  } 
}
