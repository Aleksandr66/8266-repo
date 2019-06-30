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
#include "BasicStepperDriver.h"
#define MOTOR_STEPS 200
#define RPM 240
#define MICROSTEPS 1
#define DIR D6
#define STEP D5


const char *host = "esp8266-webupdate";
const char *ssid = "Xiaomi"; // Имя роутера
const char *pass = "891261AA"; // Пароль роутера


const char *mqtt_server = "192.168.1.166"; // Имя сервера MQTT
const int mqtt_port = 1883; // Порт для подключения к серверу MQTT
const char *mqtt_user = "elgro"; //wyebltda Логи для подключения к серверу MQTT
const char *mqtt_pass = "891261AS"; //hAUHZd6r4_N_ Пароль для подключения к серверу MQTT
boolean onerun=true;
boolean oneping=true;
int pings;
int vr;
int pingsi=10000;
time_t uptime;
const int stepsPerRevolution = 200;  // change this to fit the number of steps per revolution

#define BUFFER_SIZE 100


WiFiClient wclient;
PubSubClient client(wclient, mqtt_server, mqtt_port);
ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;
BasicStepperDriver stepper(MOTOR_STEPS, DIR, STEP);

//---MQTT-------------------.length()
// Функция получения данных от сервера
void callback(const MQTT::Publish& pub)
{ 
  String payload = pub.payload_string();
  String topic = pub.topic();
  int payloadint = payload.toInt();
  String param;
  Serial.print(pub.topic()); // выводим в сериал порт название топика
  Serial.print(" => ");
  Serial.println(payload); // выводим в сериал порт значение полученных данн

  
  // проверяем из нужного ли нам топика пришли данные
  if(topic == "solution/steps"){ 
    if(payloadint >= 1){  
      stepper.move(payloadint); 
    }
  }
  if(topic == "solution/ml"){ 
    if(payloadint >= 1){  
      stepper.move(payloadint*256); 
    }
  }
  if(topic == "solution/rpm"){
    if(payloadint >= 1 && payloadint <= 350){  
      stepper.begin(payloadint, MICROSTEPS); 
    }
  }
/////////////////////////////////////////
  // проверяем из нужного ли нам топика пришли данные
  if(topic.indexOf("relay") != -1){
    //param = topic.substring(topic.lastIndexOf("/")+1, topic.length());
    //param.toCharArray(param_ch, 2);
    //payload.toCharArray(payload_ch, pl_len);
    //digitalWrite(param_ch, payload_ch);
    Serial.println("OK");
  }
}

//MqttConnect
void MQTTSetup() {
  // подключаемся к MQTT серверу
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      Serial.print("Connecting to MQTT server ");
      Serial.print(mqtt_server);
      String clientId = "ESP8266Cliental-";
      clientId += String(random(0xffff), HEX);
      Serial.println("...");
      if (client.connect(MQTT::Connect("Solution").set_auth(mqtt_user, mqtt_pass))) {
        Serial.println("Connected to MQTT server ");
        client.set_callback(callback);
        // подписываемся под топики
        client.subscribe("solution/#");
       // client.subscribe("test1/2");
      } else {
        Serial.println("Could not connect to MQTT server"); 
      }
    }   
    if (client.connected()){
      client.loop();
      //refreshData();
    } 
  }
}

//
void WifiSetup() {
  WiFi.hostname("Solution");
  // подключаемся к wi-fi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to ");
    Serial.print(ssid);
    Serial.println("...");
    WiFi.begin(ssid, pass);
    if (WiFi.waitForConnectResult() != WL_CONNECTED) return;
    Serial.println("WiFi connected");
    pinMode(LED_BUILTIN, OUTPUT);
    delay(500);
  }
}

void setup(void){
  stepper.begin(RPM, MICROSTEPS);
  Serial.begin(115200);
  Serial.println();
  Serial.println("Booting Sketch...");
  MDNS.begin(host);
  httpUpdater.setup(&httpServer);
  httpServer.begin();
  MDNS.addService("http", "tcp", 80);
  Serial.printf("HTTPUpdateServer ready! Open http://%s.local/update in your browser\n", host);
}

void loop(void){
  WifiSetup();
  MQTTSetup();
  httpServer.handleClient();
  if (millis()-uptime >= 300000 || onerun==true){
    onerun=false;
    uptime=millis();
    client.publish("soluton/uptime", String(uptime/1000));
  }
  
  delay(50);
}

//in/relay/D8 || Ping.ping(remote_ip2)
