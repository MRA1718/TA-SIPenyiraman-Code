#include "CTBot.h"
CTBot myBot;

String ssid  = "Home_9"    ; // REPLACE mySSID WITH YOUR WIFI SSID
String pass  = "Farisan2002"; // REPLACE myPassword YOUR WIFI PASSWORD, IF ANY
String token = "5482210965:AAF14_XCsdEoVlgjZL7rZpY5qf_twebh4IA"   ; // REPLACE myToken WITH YOUR TELEGRAM BOT TOKEN

void setup() {
  // initialize the Serial
  Serial.begin(115200);
  Serial.println("Starting TelegramBot...");

  // connect the ESP8266 to the desired access point
  myBot.wifiConnect(ssid, pass);

  // set the telegram bot token
  myBot.setTelegramToken(token);
  
  // check if all things are ok
  if (myBot.testConnection())
    Serial.println("\ntestConnection OK");
  else
    Serial.println("\ntestConnection NOK");
}

void loop() {
  TBMessage msg;

  if (myBot.getNewMessage(msg)) {

    if (msg.text.equalsIgnoreCase("RELAY START")) {              
      myBot.sendMessage(msg.sender.id, "RELAY is now STARTING");  //kirim pesan ke bot telegram
      Serial.print("RELAY START");
    } else {                                                    
      // membalas pesan selain kode diatas
      String reply;
      reply = (String)"Welcome " + msg.sender.username + (String)". Command: RELAY START.";
      myBot.sendMessage(msg.sender.id, reply);         
    }
  }
  
  while(Serial.available()>0){
    delay(10);
    c = Serial.read();
    data += c;
  }
  if (data.length()>0) {
    myBot.sendMessage(msg.sender.id, data);
    delay(10);
    data = "";
  }

  delay(500);
}
