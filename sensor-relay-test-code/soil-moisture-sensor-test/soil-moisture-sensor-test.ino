const int p_sTanah = 13;
const int pin_sTanah1 = A0;
const int pin_sTanah2 = A1;
int x = 0;

int senTanah(int dTanah) {
  int resTanah;
  //Sensor Tanah 1
  if(dTanah == 1){
    resTanah = analogRead(pin_sTanah1);
    return resTanah;
  } else
  //Sensor Tanah 2
  if(dTanah == 2){
    resTanah = analogRead(pin_sTanah2);
    return resTanah;
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(p_sTanah, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(p_sTanah, HIGH);
  delay(1000);
  
  while(x<10) {
    Serial.print(senTanah(1));
    Serial.print(" ");
    Serial.println(senTanah(2));
    x = x + 1;
    delay(1000);
  }

  digitalWrite(p_sTanah, LOW);

  exit(0);
}
