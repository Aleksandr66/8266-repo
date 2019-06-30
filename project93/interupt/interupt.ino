
#include <ESP8266WiFi.h>
#include <PubSubClient.h>



const char *ssid = "Xiaomi"; // Имя роутера
const char *pass = "891261AA"; // Пароль роутера

const char *mqtt_server = "192.168.1.166"; // Имя сервера MQTT
const int mqtt_port = 1883; // Порт для подключения к серверу MQTT
const char *mqtt_user = "elgro"; //wyebltda Логи для подключения к серверу MQTT
const char *mqtt_pass = "891261AS"; //hAUHZd6r4_N_ Пароль для подключения к серверу MQTT

const int led = 13; // диод на плате
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
  Serial.begin(115200);
  delay(10);  
  pinMode(pumpPin, OUTPUT);
  digitalWrite(pumpPin, HIGH); 
  Serial.println();
  Serial.println();
  pinMode (interruptPin, INPUT_PULLUP);
  attachInterrupt ( digitalPinToInterrupt (interruptPin), blink, FALLING);
}

void refreshData() {
  if (tm == 0) {
  }
  tm--;
  
  delay(1000); 
}

// Функция получения данных от сервера
void callback(const MQTT::Publish& pub)
{
  String payload = pub.payload_string();
  String topic = pub.topic();
  
  Serial.print(pub.topic()); // выводим в сериал порт название топика
  Serial.print(" => ");
  Serial.println(payload); // выводим в сериал порт значение полученных данных

  // проверяем из нужного ли нам топика пришли данные
  if(topic == "home/pump"){ 
    if(payload == "go"){  
      Serial.println("OK On");
      digitalWrite(pumpPin, LOW); 
    }
    if(payload == "off"){
      Serial.println("OK Off");
      digitalWrite(pumpPin, HIGH); 
    }
  }
}

void loop() {
  WiFi.hostname("garden");
  inn = 0;
  // подключаемся к wi-fi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to ");
    Serial.print(ssid);
    Serial.println("...");
    WiFi.begin(ssid, pass);
    
    if (WiFi.waitForConnectResult() != WL_CONNECTED) return;
    Serial.println("WiFi connected");
    pinMode(LED_BUILTIN, OUTPUT);
    while(inn < 7){
    // выполнить что-то, повторив 200 раз
    inn++;
    delay(de);
    digitalWrite(LED_BUILTIN, LOW);
    delay(de);
    digitalWrite(LED_BUILTIN, HIGH);
    }
    delay(2000);
  }
  
  // подключаемся к MQTT серверу
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      Serial.print("Connecting to MQTT server ");
      Serial.print(mqtt_server);
      String clientId = "ESP8266Client-";
      clientId += String(random(0xffff), HEX);
      Serial.println("...");
      if (client.connect(MQTT::Connect("arduinoClient3").set_auth(mqtt_user, mqtt_pass))) {
        Serial.println("Connected to MQTT server ");
        client.set_callback(callback);
        // подписываемся под топики
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
