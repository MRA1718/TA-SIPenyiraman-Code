int output_temp = 673;
void setup() {
  Serial.begin(9600); // open serial port, set the baud rate to 9600 bps
}
void loop() {
  if(output_temp > analogRead(A0)){
    output_temp = analogRead(A0);
    Serial.println(output_temp); 
  }
  else if(output_temp <= analogRead(A0)){
    Serial.print(output_temp);
    Serial.print("\t");
    Serial.println(analogRead(A0));
  }
  delay(1000);
}
