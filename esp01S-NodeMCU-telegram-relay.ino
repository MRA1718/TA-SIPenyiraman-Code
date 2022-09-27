/*
  Rui Santos .
  Complete project details at https://RandomNerdTutorials.com/telegram-control-esp32-esp8266-nodemcu-outputs/
  
  Project created using Brian Lough's Universal Telegram Bot Library: https://github.com/witnessmenow/Universal-Arduino-Telegram-Bot
  Example based on the Universal Arduino Telegram Bot Library: https://github.com/witnessmenow/Universal-Arduino-Telegram-Bot/blob/master/examples/ESP8266/FlashLED/FlashLED.ino

  Electronics and All November 2021 
  Code adapted for the ESP01s
*/


#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>   // Universal Telegram Bot Library written by Brian Lough: https://github.com/witnessmenow/Universal-Arduino-Telegram-Bot
#include <ArduinoJson.h>

// Replace with your network credentials
const char* ssid = "YOURSSID";
const char* password = "YOURPASSWORD";

// Initialize Telegram BOT 

#define BOTtoken "12345678:ABCDEFGHIJKLMNOPQRSTUV"  // your Bot Token (Get from Botfather)

// Use @myidbot to find out the chat ID of an individual or a group
// Also note that you need to click "start" on a bot before it can
// message you
#define CHAT_ID "-789101112"

X509List cert(TELEGRAM_CERTIFICATE_ROOT);

WiFiClientSecure client;
UniversalTelegramBot bot(BOTtoken, client);

// Checks for new messages every 1 second.
int botRequestDelay = 1000;
unsigned long lastTimeBotRan;
unsigned long lastMsg = 0;
 char MsgTemp[10];

const int ledPin = 2;
const short relayPin = 0;

bool ledState = HIGH;

// Handle what happens when you receive new messages
void handleNewMessages(int numNewMessages) {
  Serial.println("handleNewMessages");
  Serial.println(String(numNewMessages));

  for (int i=0; i<numNewMessages; i++) {
    // Chat id of the requester
    String chat_id = String(bot.messages[i].chat_id);
    if (chat_id != CHAT_ID){
      bot.sendMessage(chat_id, "Unauthorized user", "");
      continue;
    }
    
    // Print the received message
    String text = bot.messages[i].text;
    Serial.println(text);

    String from_name = bot.messages[i].from_name;

    if (text == "/start") {
      String welcome = "Hello, " + from_name + ".\n";
      welcome += "Use the following commands to control your outputs.\n\n";
      welcome += "/on to turn RELAY ON \n";
      welcome += "/off to turn RELAY OFF \n";
      welcome += "/? to request current RELAY state \n";
      bot.sendMessage(chat_id, welcome, "");
    }

    if (text == "/?") {
      sendMsg(MsgTemp);
    }

    if (text == "/1" || text == "/on") {
      bot.sendMessage(chat_id, "RELAY set to ON", "");
      ledState = LOW;
      digitalWrite(ledPin, ledState);
      digitalWrite(relayPin, ledState);
    }
    
    if (text == "/2" || text == "/off") {
      bot.sendMessage(chat_id, "RELAY set to OFF", "");
      ledState = HIGH;
      digitalWrite(ledPin, ledState);
      digitalWrite(relayPin, ledState);
    }
    
    if (text == "/?") {
      if (digitalRead(ledPin)){
        bot.sendMessage(chat_id, "RELAY is OFF", "");
      }
      else{
        bot.sendMessage(chat_id, "RELAY is ON", "");
      }
    }
    if (text == "/p") {
      
      ledState = LOW;
      digitalWrite(ledPin, ledState);
      digitalWrite(relayPin, ledState);
      delay(1000);
      ledState = HIGH;
      digitalWrite(ledPin, ledState);
      digitalWrite(relayPin, ledState);
      bot.sendMessage(chat_id, "RELAY pulsed", "");
    }
  }
}

void setup() {
  Serial.begin(115200);

    configTime(0, 0, "pool.ntp.org");      // get UTC time via NTP
    client.setTrustAnchors(&cert); // Add root certificate for api.telegram.org

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, ledState);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, ledState);
  
  // Connect to Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
  // Print ESP32 Local IP Address
  Serial.println(WiFi.localIP());
}

void sendMsg(char msg []){
   bot.sendMessage(CHAT_ID,msg,"");
}

void loop() {
  if (millis() > lastTimeBotRan + botRequestDelay)  {
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);

    while(numNewMessages) {
      Serial.println("got response");
      handleNewMessages(numNewMessages);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    }
    lastTimeBotRan = millis();

     unsigned long Millis = millis();
  if (Millis - lastMsg > 30000)
  {
    lastMsg = Millis;
  }
  }
}