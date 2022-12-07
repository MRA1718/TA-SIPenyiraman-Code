int output_temp = 673;

const int power_sTanah = 9;
const int sTanah1_pin = A0;
const int sTanah2_pin = A1;
int dsTanah1, dsTanah2;

int sTanah(int dTanah) {
  int res;
  if(dTanah == 1){
    res = analogRead(sTanah1_pin);
    return res; 
  } else
  if(dTanah == 2){
    res = analogRead(sTanah2_pin);
    return res;
  }
}

void setup() {
  Serial.begin(115200); 
  pinMode(power_sTanah, OUTPUT);
}

char txt = 0;

void loop() {
  /*if (Serial.available() > 0) {
    txt = Serial.read();

    if (txt == '1')  {*/
      String rep;
      digitalWrite(power_sTanah, HIGH);
      //Serial.println("sensor power on");
      dsTanah1 = sTanah(1); 
      dsTanah2 = sTanah(2);
      //digitalWrite(power_sTanah, LOW);
      //Serial.println("sensor power off");
      rep = (String) "sensor tanah 1: " + dsTanah1 + ", sensor tanah 2: " + dsTanah2;
      Serial.println(rep);
    //}
  //}
  
  delay(1000);
}
