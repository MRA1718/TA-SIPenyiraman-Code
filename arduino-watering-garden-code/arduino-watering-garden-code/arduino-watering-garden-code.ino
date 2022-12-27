#include <ArduinoJson.h>
#include <DFRobot_DHT20.h>


DFRobot_DHT20 dht20;
String data;
char c;
const int power = 13;
const int senSoilPin1 = A0;
const int senSoilPin2 = A1;
const int senLightPin = A2;
const int waterMoistVal = 55;
const int airMoistVal = 650;
StaticJsonDocument<64> doc;
int s1, s2, l;
float t, h, sc1, sc2;

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
    rTempt = (dht20.getTemperature());
    return rTempt;
  } else
  if(dTempt == 2) {
    rTempt = (dht20.getHumidity()*100);
    return rTempt;
  }
}

float mapf(float x, float in_min, float in_max, float out_min, float out_max)
{
  float mRes;
  mRes = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  return mRes;
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
    sc1 = mapf(s1, airMoistVal, waterMoistVal, 0.0, 100.0);
    s2 = senSoil(2);
    sc2 = mapf(s2, airMoistVal, waterMoistVal, 0.0, 100.0);   
    //fetch data Temperature Sensor
    if(!dht20.begin()){
      t = senTempt(1);
      h = senTempt(2);
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
