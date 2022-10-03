void setup() {
  // put your setup code here, to run once:
Serial.begin(115200);

    String data = "START PUMP 3";
    int data_len = data.length() + 1;
    String data_array[data_len];
    int dataCount = 0;
    //data.toCharArray(data_array, data_len);

    Serial.println(data_len);

    while (data.length() > 0) {
      int index = data.indexOf(' ');
      if (index == -1) // No space found
      {
        data_array[dataCount++] = data;
        break;
      } else {
        data_array[dataCount++] = data.substring(0, index);
        data = data.substring(index+1);
      }
    }

    Serial.println(dataCount);
    
    for (int i=0; i < dataCount; i++) {
      Serial.println(data_array[i]);
    }
    //Serial.println(data_array[11]);
}

void loop() {
  // put your main code here, to run repeatedly:
    
  
}
