//Welcome
//Electronics University

const int airMoisVal = 675;
const int waterMoisVal = 70;
const int relayPin = 5;
int soilPin = A0; // Soil Sensor input at Analog PIN A0
int output_value;
void setup()         // put your setup code here, to run once:
{ 
  Serial.begin(115200);                 
  pinMode(relayPin, OUTPUT);
  pinMode(soilPin, INPUT);
  Serial.println("Reading From the Sensor ...");
  delay(2000);
}

void loop()
{
 output_value= analogRead(soilPin);
 output_value= map(output_value,airMoisVal,waterMoisVal,0,100);
 Serial.print("Mositure in RH : ");
 Serial.print(output_value);
 Serial.print("%\t");
 Serial.print("Sensor Value:");
 Serial.println(analogRead(soilPin));
 
 if(output_value<=70){
  digitalWrite(relayPin, HIGH);
 }
 else
 {
  digitalWrite(relayPin, LOW);       
 }
 delay(1000);
}
