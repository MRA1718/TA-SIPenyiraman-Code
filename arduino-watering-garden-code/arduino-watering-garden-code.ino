#include <DFRobot_DHT20.h>
#include <SoftwareSerial.h>

SoftwareSerial mySerial(2,3);
DFROBOT_DHT20 dht20;
String data, rep;
char c;
const int power = 13;
const int sTanah1_pin = A0;
const int sTanah2_pin = A1;
const int sCahaya_pin = A2;

int dsTanah1, dsTanah2;
float dsSuhu1, dsSuhu2;
int dsCahaya;
int res;

//Sensor Tanah
int senTanah(int dTanah) {
  int resTanah;
  //Sensor Tanah 1
  if(dTanah == 1){
    digitalWrite(power_sTanah, HIGH);
    delay(1000);
    resTanah = analogRead(sTanah1_pin);
    digitalWrite(power_sTanah, LOW);
    return resTanah;
  } else
  //Sensor Tanah 2
  if(dTanah == 2){
    digitalWrite(power_sTanah, HIGH);
    delay(5000);
    resTanah = analogRead(sTanah2_pin);
    digitalWrite(power_sTanah, LOW);
    return resTanah;
  }
}
//Sensor Suhu & Kelembaban
float senSuhu(int dSuhu)  {
  float resSuhu;
  //Suhu
  if(dSuhu == 1){
    digitalWrite(power_sSuhu, HIGH);
    delay(1000);
    resSuhu = dht20.getTemperature();
    digitalWrite(power_sSuhu, LOW);
    return resSuhu;
  } else
  //Kelembaban Udara
  if (dSuhu == 2) {
    digitalWrite(power_sSuhu, HIGH);
    delay(1000);
    resSuhu = dht20.getHumidity()*100;
    digitalWrite(power_sSuhu, LOW);
    return resSuhu;
  }
}

//Sensor Cahaya
int senCahaya() {
  int resCahaya;

  resCahaya = analogRead(A2);
  return resCahaya;
}

void setup() {
  Serial.begin(115200);
  mySerial.begin(115200);
  
  pinMode(relay_pin, OUTPUT);
  pinMode(power_sTanah, OUTPUT);
  pinMode(power_sSuhu, OUTPUT);
  pinMode(power_sCahaya, OUTPUT);
  
 }

void loop() {
  while(mySerial.available()>0){
    delay(10);
    c = mySerial.read();
    data += c;
  }   
  if (data.length()>0) {
    Serial.println(data);
    /*if (data == "nyalakan pompa") {
      digitalWrite(relay_pin, HIGH);
      mySerial.print("pompa menyala");
      delay(180000);
      digitalWrite(relay_pin, LOW);
      mySerial.print("pompa mati");
    } else */
    if (data == "sensor tanah") {
      //digitalWrite(power_sTanah, HIGH);
      dsTanah1 = senTanah(1); 
      dsTanah2 = senTanah(2);
      //digitalWrite(power_sTanah, LOW);
      rep = (String) "sensor tanah 1: " + dsTanah1 + ", sensor tanah 2: " + dsTanah2;
      mySerial.print(rep);
    } else
    if(data == "sensor suhu") {
      dsSuhu1 = senSuhu(1);
      dsSuhu2 = senSuhu(2);

      rep = (String) "sensor suhu: " + dsSuhu1 + "C dan kelembaban relatif: " + dsSuhu2 "%RH";
      mySerial.print(rep);
    }
    data = "";
  }
}
