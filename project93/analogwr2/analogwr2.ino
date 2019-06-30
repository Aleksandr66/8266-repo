#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>

const char *ssid = "Xiaomi"; // РРјСЏ СЂРѕСѓС‚РµСЂР°
const char *pass = "891261AA"; // РџР°СЂРѕР»СЊ СЂРѕСѓС‚РµСЂР°

//To make Arduino software autodetect OTA device
WiFiServer TelnetServer(8266);

const char *mqtt_server = "192.168.1.166"; // РРјСЏ СЃРµСЂРІРµСЂР° MQTT
const int mqtt_port = 1883; // РџРѕСЂС‚ РґР»СЏ РїРѕРґРєР»СЋС‡РµРЅРёСЏ Рє СЃРµСЂРІРµСЂСѓ MQTT
const char *mqtt_user = "elgro"; //wyebltda Р›РѕРіРё РґР»СЏ РїРѕРґРєР»СЋС‡РµРЅРёСЏ Рє СЃРµСЂРІРµСЂСѓ MQTT
const char *mqtt_pass = "891261AS"; //hAUHZd6r4_N_ РџР°СЂРѕР»СЊ РґР»СЏ РїРѕРґРєР»СЋС‡РµРЅРёСЏ Рє СЃРµСЂРІРµСЂСѓ MQTT
int dim = 0;
int green = 0;
int red = 0;
int blue = 0;
String vrgb;
const int led = 13; // РґРёРѕРґ РЅР° РїР»Р°С‚Рµ
const int de = 55;
float inn = 0;
#define BUFFER_SIZE 100
const byte interruptPin = D5;
const byte pumpPin = D2;
int tm = 300;
float temp = 0;

WiFiClient wclient; 
PubSubClient client(wclient, mqtt_server, mqtt_port);

void setup() {

  TelnetServer.begin();
  Serial.begin(115200);
  delay(10);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
  pinMode(D8, OUTPUT);
  analogWriteFreq(300);
  //pinMode(pumpPin, OUTPUT);
  //digitalWrite(pumpPin, HIGH); 
  Serial.println();
  Serial.println();
  //pinMode (interruptPin, INPUT_PULLUP);
  //attachInterrupt ( digitalPinToInterrupt (interruptPin), blink, FALLING);
  ArduinoOTA.onStart([]() {
    Serial.println("OTA Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("OTA End");
    Serial.println("Rebooting...");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r\n", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.begin();
}

void refreshData() {
  if (tm == 0) {
  }
  tm--;
  
  delay(100); 
}

// Р¤СѓРЅРєС†РёСЏ РїРѕР»СѓС‡РµРЅРёСЏ РґР°РЅРЅС‹С… РѕС‚ СЃРµСЂРІРµСЂР°
void callback(const MQTT::Publish& pub)
{
  String payload = pub.payload_string();
  String topic = pub.topic();
  
  Serial.print(pub.topic()); // РІС‹РІРѕРґРёРј РІ СЃРµСЂРёР°Р» РїРѕСЂС‚ РЅР°Р·РІР°РЅРёРµ С‚РѕРїРёРєР°
  Serial.print(" => ");
  Serial.println(payload); // РІС‹РІРѕРґРёРј РІ СЃРµСЂРёР°Р» РїРѕСЂС‚ Р·РЅР°С‡РµРЅРёРµ РїРѕР»СѓС‡РµРЅРЅС‹С… РґР°РЅРЅС‹С…
  // РїСЂРѕРІРµСЂСЏРµРј РёР· РЅСѓР¶РЅРѕРіРѕ Р»Рё РЅР°Рј С‚РѕРїРёРєР° РїСЂРёС€Р»Рё РґР°РЅРЅС‹Рµ
  if(topic == "home/led/br"){
    int  pload= payload.toInt();
    if(pload > dim){
      for (int i=dim; i<=pload; i++){
        analogWrite(D5, i);
        delay(3);
      }
      //Serial.println("OK On");
      //digitalWrite(pumpPin, LOW); 
    }else{
      for (int i=dim; i>=pload; i=i-1){
        analogWrite(D5, i);
        delay(3);
      }
    }
    dim = pload;
    if(payload == "off"){
      Serial.println("OK Off");
      digitalWrite(pumpPin, HIGH); 
    }
  }
  if(topic == "home/led/rgb"){

   vrgb=payload;
   long number = (long) strtol( &vrgb[1], NULL, 16);
   red = number >> 16;
   green = number >> 8 & 0xFF;
   blue = number & 0xFF;
   //const char ledr=strtok(payload.c_str(), ", ");
   //const char ledg=strtok(NULL, ", ");
   //const char ledB=strtok(NULL, ", "));
   analogWrite(D6, green*4);
   analogWrite(D7, red*4);
   analogWrite(D8, blue*4);
   
  //analogWriteFreq(payload.toInt());  
  }
}

void loop() {
  ArduinoOTA.handle();
  WiFi.hostname("garden");
  inn = 0;
  // РїРѕРґРєР»СЋС‡Р°РµРјСЃСЏ Рє wi-fi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to ");
    Serial.print(ssid);
    Serial.println("...");
    WiFi.begin(ssid, pass);
    
    if (WiFi.waitForConnectResult() != WL_CONNECTED) return;
    Serial.println("WiFi connected");
    pinMode(LED_BUILTIN, OUTPUT);
    while(inn < 7){
    // РІС‹РїРѕР»РЅРёС‚СЊ С‡С‚Рѕ-С‚Рѕ, РїРѕРІС‚РѕСЂРёРІ 200 СЂР°Р·
    inn++;
    delay(de);
    digitalWrite(LED_BUILTIN, LOW);
    delay(de);
    digitalWrite(LED_BUILTIN, HIGH);
    }
    delay(2000);
  }
  
  // РїРѕРґРєР»СЋС‡Р°РµРјСЃСЏ Рє MQTT СЃРµСЂРІРµСЂСѓ
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      Serial.print("Connecting to MQTT server ");
      Serial.print(mqtt_server);
      String clientId = "ESP8266Client-";
      clientId += String(random(0xffff), HEX);
      Serial.println("...");
      if (client.connect(MQTT::Connect("arduinoClient34").set_auth(mqtt_user, mqtt_pass))) {
        Serial.println("Connected to MQTT server ");
        client.set_callback(callback);
        // РїРѕРґРїРёСЃС‹РІР°РµРјСЃСЏ РїРѕРґ С‚РѕРїРёРєРё
        client.subscribe("#");
       // client.subscribe("test1/2");
      } else {
        Serial.println("Could not connect to MQTT server"); 
      }
    }
    
    if (client.connected()){
      client.loop();
      refreshData();
    }
  
  }
}

void blink () {
digitalWrite(pumpPin, HIGH);
}

