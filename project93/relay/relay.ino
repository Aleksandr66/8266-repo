
#include <ESP8266WiFi.h>
#include <PubSubClient.h>



const char *ssid = "Xiaomi"; // Имя роутера
const char *pass = "891261AA"; // Пароль роутера

const char *mqtt_server = "m20.cloudmqtt.com"; // Имя сервера MQTT
const int mqtt_port = 18832; // Порт для подключения к серверу MQTT
const char *mqtt_user = "Xupypr"; //wyebltda Логи для подключения к серверу MQTT
const char *mqtt_pass = "891261"; //hAUHZd6r4_N_ Пароль для подключения к серверу MQTT

const int led = 13; // диод на плате
const int de = 55;
float inn = 0;
#define BUFFER_SIZE 100

int tm = 300;
float temp = 0;

WiFiClient wclient; 
PubSubClient client(wclient, mqtt_server, mqtt_port);

void setup() {
  Serial.begin(115200);
  delay(10);

  Serial.println();
  Serial.println();

  
}

void refreshData() {
  if (tm == 0) {
    float h = dht.readHumidity();
    delay(1000);
    float t = dht.readTemperature();
    String temperature = String(t);
    String humidity = String(h);
    client.publish("test/1", temperature);
    client.publish("test/2", humidity);
    tm = 3; // пауза меду отправками 3 секунды
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
  pinMode(5, OUTPUT);
  // проверяем из нужного ли нам топика пришли данные
  if(topic == "test"){ 
    if(payload == "on"){  
      Serial.println("OK On");
      digitalWrite(16, HIGH); 
    }
    if(payload == "off"){
      Serial.println("OK Off");
      digitalWrite(16, LOW); 
    }
  }
}

void loop() {
  WiFi.hostname("Light");
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
    float h = dht.readHumidity();
    delay(2000);
    float t = dht.readTemperature();
    delay(2000);
    Serial.println(t);
    Serial.println(h);
  }
  
  // подключаемся к MQTT серверу
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      Serial.print("Connecting to MQTT server ");
      Serial.print(mqtt_server);
      Serial.println("...");
      if (client.connect(MQTT::Connect("arduinoClient2").set_auth(mqtt_user, mqtt_pass))) {
        Serial.println("Connected to MQTT server ");
        client.set_callback(callback);
        // подписываемся под топики
        client.subscribe("test");
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
