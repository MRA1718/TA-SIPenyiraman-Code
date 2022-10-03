void setup() {
  // put your setup code here, to run once:
Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
    String data = "START PUMP 3";
    int data_len = data.length() + 1;
    char data_array[data_len];
    data.toCharArray(data_array, data_len);

    for (

}
