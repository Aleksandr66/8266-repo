
/*
  To upload through terminal you can use: curl -F "image=@firmware.bin" esp8266-webupdate.local/update
*/

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>
#include <PubSubClient.h>
#include <TimeLib.h>

const char *host = "esp8266-webupdate";
const char *ssid = "Xiaomi"; // Имя роутера
const char *pass = "891261AA"; // Пароль роутера


const char* mqtt_server = "m15.cloudmqtt.com";
const int mqtt_port = 13843;
const char* mqtt_user = "mgtiorid";
const char* mqtt_pass = "WOVVw2j9Rm2t";
//
long lastMsg = 0;
char msg[50];
int value = 0;

/*const char *mqtt_server = "192.168.1.166"; // Имя сервера MQTT
  const int mqtt_port = 1883; // Порт для подключения к серверу MQTT
  const char *mqtt_user = "elgro"; //wyebltda Логи для подключения к серверу MQTT
  const char *mqtt_pass = "891261AS"; //hAUHZd6r4_N_ Пароль для подключения к серверу MQTT
  boolean onerun=true;
  boolean oneping=true;
  int pings;
  int vr;
  int pingsi=10000;
*/
long state, uptime, rec;
byte gpi[] = {D0, D1, D2, D3, D4, D5, D6, D7, D8};
boolean gpii[] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

//#define BUFFER_SIZE 100

WiFiClient espClient;
PubSubClient client(espClient);
ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;


void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Booting Sketch...");
  delay(10);
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
  pinMode(D8, OUTPUT);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  MDNS.begin(host);
  httpUpdater.setup(&httpServer);
  httpServer.begin();
  MDNS.addService("http", "tcp", 80);
  Serial.printf("HTTPUpdateServer ready! Open http://%s.local/update in your browser\n", host);
  WifiSetup();
  reconnect();
}

void loop() {

  client.loop();
  httpServer.handleClient();
  if (millis() - rec >= 60000) {
    rec = millis();
    WifiSetup();
    reconnect();
  }
  if (millis() - uptime >= 300000) {
    uptime = millis();
    client.publish("out/uptime", String(uptime).c_str(), true);
  }
  if (millis() - state >= 200) {
    for (int i = 1; i <= 8; i++) {
      if (digitalRead(gpi[i]) == !gpii[i]) {
        gpii[i] = digitalRead(gpi[i]);
        if (digitalRead(gpi[i]) == LOW) {
          client.publish(("out/state/D" + String(i)).c_str() , "off", true);
        }
        if (digitalRead(gpi[i]) == HIGH) {
          client.publish(("out/state/D" + String(i)).c_str() , "on", true);
        }
      }
    }
    state = millis();
  }
  //delay(50);
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String pload, tpic;
  tpic=String(topic);
  for (int i = 0; i < length; i++) {
    //Serial.print((char)payload[i]);
    pload += char(payload[i]);

  }
  Serial.print(pload);
  Serial.println();

  if (tpic == "in/relay/all") {
    if (pload == "off") {
      Serial.println("all Off");
      for (int i = 0; i < 8; i++) {
        digitalWrite(gpi[i], LOW);
      }
    }
    if (pload == "on") {
      Serial.println("all On");
      for (int i = 0; i < 8; i++) {
        digitalWrite(gpi[i], HIGH);
      }
    }
  }
  // проверяем из нужного ли нам топика пришли данные
  if (tpic.indexOf("relay")  != -1) {
    if (pload == "on") {
      digitalWrite(gpi[tpic.substring(tpic.length()-1,tpic.length()).toInt()], HIGH);
    }
    if (pload == "off") {
      digitalWrite(gpi[tpic.substring(tpic.length()-1,tpic.length()).toInt()], LOW);
    }
  }
}
void WifiSetup() {
  WiFi.hostname("Dimon");
  // подключаемся к wi-fi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to ");
    Serial.print(ssid);
    Serial.println("...");
    WiFi.begin(ssid, pass);
    if (WiFi.waitForConnectResult() != WL_CONNECTED) return;
    Serial.println("WiFi connected");
    //pinMode(LED_BUILTIN, OUTPUT);
    delay(500);
  }
}

void reconnect() {
  // Loop until we're reconnected
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
      // Create a random client ID
      String clientId = "ESP8266Client-";
      clientId += String(random(0xffff), HEX);
      // Attempt to connect
      if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
        Serial.println("connected");
        // Once connected, publish an announcement...
        //client.publish("outTopic", "hello world");
        // ... and resubscribe
        client.subscribe("in/#");
      } else {
        Serial.println("Could not connect to MQTT server");
      }
    } else {
      //client.loop();
    }
  }
}
//in/relay/D8 || Ping.ping(remote_ip2)
