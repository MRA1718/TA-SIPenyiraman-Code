#include <DFRobot_DHT20.h>

DFRobot_DHT20 dht20;
const int p_sTemp = 13;
int x = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(p_sTemp, OUTPUT);
  
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(p_sTemp, HIGH);
  Serial.println("power on");
  delay(1000);

  if(!dht20.begin()){
    Serial.println("Initialize sensor success");
    delay(1000);
  }
    
  while(x<10) {
    Serial.print("temperature:"); Serial.print(dht20.getTemperature());Serial.print("C");
    Serial.print("  humidity:"); Serial.print(dht20.getHumidity()*100);Serial.println(" %RH");
    x = x + 1;
    delay(1000);
  }

  digitalWrite(p_sTemp, LOW);
  Serial.println("power off");
  delay(1000);

  exit(0);
}
