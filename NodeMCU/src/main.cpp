#include <Arduino.h>
#include <ESP8266WiFi.h>

#define NOT_CONNECT 3
#define MAXLEN 20

const char* ssid = "TARDIS";
const char* password = "PraiaPeruibe";

typedef struct msg_ {
  char buffer[20];
  int size;
} msg;

WiFiServer wifiServer(80);

msg message;

void blink_error_code (int n) {
  while(1) {
    for(int i = 0; i < n; i++){
      digitalWrite(D0, HIGH);
      delay(200);
      digitalWrite(D0, LOW);
      delay(200);
    }
    delay(1000);
  }
}

bool connection_handler(WiFiClient client) {
  if (client) {
    while (client.connected()) {
      int index = 0;
      while(client.available() && index < MAXLEN) {
            char c = client.read();
            message.buffer[index] = c;
            index++;
      }
      if(index > 0) {
        message.buffer[index] = '\0';
        message.size = index-1;
        Serial.print("A string: " +String(message.buffer));
        client.flush();
        client.write("End Transmission\n");
      }
    }
    client.stop();
    Serial.println("[+] Client disconnected");
    return 1;
  }
  else return 0;
}

void setup() {
  pinMode(D0, OUTPUT);
  pinMode(D1, OUTPUT);
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("[+] Connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(5000);
  }

  if(WiFi.status() != WL_CONNECTED) {
    Serial.println("[Error] Not connected to wifi!");
    blink_error_code (NOT_CONNECT);
  }

  Serial.print("[+] Connected to WiFi. IP:");
  Serial.println(WiFi.localIP());
  wifiServer.begin();
}

void parser_command () {
  String cmd = String(message.buffer);
  Serial.println(String(cmd) + " " + String(message.size));
  if(message.size == 6) {
    if(cmd.substring(0,3) == "LED") {
      int led = String(cmd.substring(3,5)).toInt();
      Serial.println(String(D1) + " " + String(D0));
      //Serial.println(led);
      //Serial.println((cmd[5]-'0'));
      digitalWrite(led, (cmd[5]-'0'));
    }
  }
  else Serial.println("CMD not valid");
}

void loop() {
  WiFiClient client = wifiServer.available();
  if(connection_handler(client)) parser_command();
}
