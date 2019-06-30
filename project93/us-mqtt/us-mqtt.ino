
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#define echoPin D7
#define trigPin D6
long duration, distance;


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
int chek=0;
int tm = 300;
float temp = 0;
int ln=0;
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
    delay(10);
    int saved=dist();
    
    client.publish("home/sensor/dist", String(saved));
    tm = 3000; // пауза меду отправками 3 секунды
    if (saved<ln && chek==0){
      client.publish("home/relay/n1", "off");
      chek=1;
      }
    if (saved>ln && chek==1){
      client.publish("home/relay/n1", "on");
      chek=0;
      }
  }
  tm--;

  delay(1);
}

int dist() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  delay(10);
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = duration / 58.2;
  Serial.println(distance);
  return distance;
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
  if (topic == "home/sensor/dist/ln") {
    ln=payload.toInt();
    if (payload == "on") {
      Serial.println("OK On");
      digitalWrite(5, HIGH);
    }
    if (payload == "off") {
      Serial.println("OK Off");
      digitalWrite(5, LOW);
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
    while (inn < 7) {
      // выполнить что-то, повторив 200 раз
      inn++;
      delay(de);
      digitalWrite(LED_BUILTIN, LOW);
      delay(de);
      digitalWrite(LED_BUILTIN, HIGH);
    }
  }

  // подключаемся к MQTT серверу
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      Serial.print("Connecting to MQTT server ");
      Serial.print(mqtt_server);
      Serial.println("...");
      if (client.connect(MQTT::Connect("arduinoClient5").set_auth(mqtt_user, mqtt_pass))) {
        Serial.println("Connected to MQTT server ");
        client.set_callback(callback);
        // подписываемся под топики
        client.subscribe("#");
        // client.subscribe("test1/2");
      } else {
        Serial.println("Could not connect to MQTT server");
      }
    }

    if (client.connected()) {
      client.loop();
      refreshData();
    }

  }
}
