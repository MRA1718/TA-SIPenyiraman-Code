#include "CTBot.h"
CTBot myBot;

String ssid  = "Home_9"    ; // REPLACE mySSID WITH YOUR WIFI SSID
String pass  = "Farisan2002"; // REPLACE myPassword YOUR WIFI PASSWORD, IF ANY
String token = "5725314127:AAHxruba6S34B0He6rQ8vVRlJ6IZ_0ucgQ4"   ; // REPLACE myToken WITH YOUR TELEGRAM BOT TOKEN

String data;
char c;

void setup() {
  // initialize the Serial
  Serial.begin(115200);
  Serial.println("Starting TelegramBot...");

  // connect the ESP8266 to the desired access point
  myBot.wifiConnect(ssid, pass);
  //myBot.setIP("192.168.1.111", "192.168.1.1", "255.255.255.0");
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
    if (msg.text.equalsIgnoreCase("nyalakan pompa")) {              
      myBot.sendMessage(msg.sender.id, "pompa akan menyala selama 3 menit");  //kirim pesan ke bot telegram
      Serial.print("nyalakan pompa");
    } else 
    if (msg.text.equalsIgnoreCase("sensor tanah"))  {
      myBot.sendMessage(msg.sender.id, "membaca sensor tanah");
      Serial.print("sensor tanah");
    } else
    if (msg.text.equalsIgnoreCase("sensor suhu"))  {
      myBot.sendMessage(msg.sender.id, "membaca sensor suhu dan kelembaban");
      Serial.print("sensor SH");
    } else
    if (msg.text.equalsIgnoreCase("sensor cahaya"))  {
      myBot.sendMessage(msg.sender.id, "membaca sensor cahaya");
      Serial.print("sensor cahaya");
    } else
    if (msg.text.equalsIgnoreCase("/start")){                                                    
      // membalas pesan selain kode diatas
      String reply;
      reply = (String)"Halo " + msg.sender.username + (String)". Perintah: nyalakan pompa.";
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
