#include "CTBot.h"
CTBot myBot;

const char* ssid = "Home_9";
const char* pass = "Farisan2002";
const char*  token = "5482210965:AAF14_XCsdEoVlgjZL7rZpY5qf_twebh4IA";

String data;
char c;

void setup() {
  Serial.begin(115200);
  Serial.println("\nStarting TelegramBot...");

  myBot.wifiConnect(ssid, pass);

  myBot.setTelegramToken(token);

  // check if all things are ok
  if (myBot.testConnection())
    Serial.println("\ntestConnection OK");
  else
    Serial.println("\ntestConnection FAILED");

}

void loop() {
  TBMessage msg;

  if (myBot.getNewMessage(msg)) {

    if (msg.text.equalsIgnoreCase("RELAY START")) {
      myBot.sendMessage(msg.sender.id, "RELAY is now STARTING");  //kirim pesan ke bot telegram
      Serial.print("RELAY START");
    }
    else {
      // membalas pesan selain kode diatas
      String reply;
      reply = (String)"Welcome " + msg.sender.username + (String)". Command: RELAY ON, RELAY OFF, TEMPERATURE.";
      myBot.sendMessage(msg.sender.id, reply);
    }
  }

  while (Serial.available() > 0) {
    delay(10);
    c = Serial.read();
    data += c;
  }
  if (data.length() > 0) {
    myBot.sendMessage(msg.sender.id, data + " Celcius Degrees");
    delay(10);
    data = "";
  }

  delay(500);
}
