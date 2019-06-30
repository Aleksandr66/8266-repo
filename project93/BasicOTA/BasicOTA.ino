#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>
//-MQTT-----------------------------------------
const char *mqtt_server = "m15.cloudmqtt.com"; // Имя сервера MQTT
const int mqtt_port = 13843; // Порт для подключения к серверу MQTT
const char *mqtt_user = "mgtiorid"; //Логи для подключения к серверу MQTT
const char *mqtt_pass = "WOVVw2j9Rm2t"; //Пароль для подключения к серверу MQTT

// вписываем здесь SSID и пароль для вашей WiFi-сети:
const char* ssid = "Xiaomi";  // название Wi-Fi сети
const char* pass = "891261AA";  // пароль сети
WiFiClient wclient; 
PubSubClient client(wclient, mqtt_server, mqtt_port);
void callback(const MQTT::Publish& pub)
{
  String payload = pub.payload_string();
  String topic = pub.topic();
  String param;
  Serial.print(pub.topic()); // выводим в сериал порт название топика
  Serial.print(" => ");
  Serial.println(payload); // выводим в сериал порт значение полученных данн
  
  // проверяем из нужного ли нам топика пришли данные
  if(topic.indexOf("param") != -1){
    param = topic.substring(topic.lastIndexOf("/")+1, topic.length());
    if (param=="itm"){
      //itm=payload.toInt();
    }else if(param=="ipmp"){
      //ipmp=payload.toInt();  
    }
    Serial.println("Set new param"); 
    if(payload == "on"){  
      
    }
    if(payload == "off"){
      Serial.println("OK Off"); 
    }
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
      if (client.connect(MQTT::Connect("arduinoClient356").set_auth(mqtt_user, mqtt_pass))) {
        Serial.println("Connected to MQTT server ");
        client.set_callback(callback);
        // подписываемся под топики
        client.subscribe("in/#");
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
  WiFi.hostname("ProjectLOP");
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

void setup() {
  Serial.begin(115200);
  Serial.println("Booting");
 

  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);

  // Hostname defaults to esp8266-[ChipID]
  // ArduinoOTA.setHostname("myesp8266");

  // No authentication by default
  // ArduinoOTA.setPassword((const char *)"123");

  ArduinoOTA.onStart([]() {
    Serial.println("Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
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
  ArduinoOTA.setHostname("Valera");
  Serial.println("Ready");
}

void loop() {
  WifiSetup();
  MQTTSetup();
  ArduinoOTA.handle();
}
