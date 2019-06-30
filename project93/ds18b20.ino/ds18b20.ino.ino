/*********
  Руи Сантос (Rui Santos)
  Более подробно о проекте на: http://randomnerdtutorials.com
*********/

// подключаем библиотеку «ESP8266WiFi»:
#include <ESP8266WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <PubSubClient.h>



//------------------------------------------
//DS18B20
#define ONE_WIRE_BUS D3 //Pin to which is attached a temperature sensor
#define ONE_WIRE_MAX_DEV 15 //The maximum number of devices

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature DS18B20(&oneWire);
int numberOfDevices; //Number of temperature devices found
DeviceAddress devAddr[ONE_WIRE_MAX_DEV];  //An array device temperature sensors
float tempDev[ONE_WIRE_MAX_DEV]; //Saving the last measurement of temperature
float tempDevLast[ONE_WIRE_MAX_DEV]; //Previous temperature measurement
long lastTemp; //The last measurement
const int durationTemp = 5000; //The frequency of temperature measurement

//-MQTT-----------------------------------------
const char *mqtt_server = "m15.cloudmqtt.com"; // Имя сервера MQTT
const int mqtt_port = 13843; // Порт для подключения к серверу MQTT
const char *mqtt_user = "mgtiorid"; //Логи для подключения к серверу MQTT
const char *mqtt_pass = "WOVVw2j9Rm2t"; //Пароль для подключения к серверу MQTT

// вписываем здесь SSID и пароль для вашей WiFi-сети:
const char* ssid = "Xiaomi";  // название Wi-Fi сети
const char* pass = "891261AA";  // пароль сети

//-ElBRO-----------------------------------------
int pmptime;
float temp_C1, temp_C2;
int tmi; 
int pmpi= 0;
int itm = 3;
int ipmp = 30;
boolean onemsg = false;
const byte interruptPin2 = D8;

WiFiClient wclient; 
PubSubClient client(wclient, mqtt_server, mqtt_port);

//Convert device id to String
String GetAddressToString(DeviceAddress deviceAddress) {
  String str = "";
  for (uint8_t i = 0; i < 8; i++) {
    if ( deviceAddress[i] < 16 ) str += String(0, HEX);
    str += String(deviceAddress[i], HEX);
  }
  return str;
}


//---MQTT-------------------.length()
// Функция получения данных от сервера
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
      itm=payload.toInt();
    }else if(param=="ipmp"){
      ipmp=payload.toInt();  
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
      if (client.connect(MQTT::Connect("arduinoClient3").set_auth(mqtt_user, mqtt_pass))) {
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
  WiFi.hostname("Dimon");
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
//Setting the temperature sensor
void SetupDS18B20() {
  DS18B20.begin();

  Serial.print("Parasite power is: ");
  if ( DS18B20.isParasitePowerMode() ) {
    Serial.println("ON");
  } else {
    Serial.println("OFF");
  }

  numberOfDevices = DS18B20.getDeviceCount();
  Serial.print( "Device count: " );
  Serial.println( numberOfDevices );

  lastTemp = millis();
  DS18B20.requestTemperatures();

  // Loop through each device, print out address
  for (int i = 0; i < numberOfDevices; i++) {
    // Search the wire for address
    if ( DS18B20.getAddress(devAddr[i], i) ) {
      //devAddr[i] = tempDeviceAddress;
      Serial.print("Found device ");
      Serial.print(i, DEC);
      Serial.print(" with address: " + GetAddressToString(devAddr[i]));
      Serial.println();
    } else {
      Serial.print("Found ghost device at ");
      Serial.print(i, DEC);
      Serial.print(" but could not detect address. Check power and cabling");
    }

    //Get resolution of DS18b20
    Serial.print("Resolution: ");
    Serial.print(DS18B20.getResolution( devAddr[i] ));
    Serial.println();

    //Read temperature from DS18b20
    float tempC = DS18B20.getTempC( devAddr[i] );
    Serial.print("Temp C: ");
    Serial.println(tempC);
  }
}

// блок setup() запускается только один раз – при загрузке:
void setup() {
  // инициализируем последовательный порт (для отладочных целей):
  Serial.begin(115200);
  delay(10);
  pinMode(D4, OUTPUT);
  digitalWrite(D4, HIGH);
  pinMode(D5, OUTPUT);
  digitalWrite(D5, HIGH);
  pinMode (D7, INPUT_PULLUP);
  //attachInterrupt (D8, blink, FALLING);//digitalPinToInterrupt (interruptPin2)
  SetupDS18B20();
}





// блок loop() будет запускаться снова и снова:
void loop() {
  WifiSetup();
  MQTTSetup();
  if (tmi>=itm*10){
    tmi=0;
    DS18B20.requestTemperatures();
    temp_C1 = DS18B20.getTempC( devAddr[0] );
    temp_C2 = DS18B20.getTempC( devAddr[1] );
    client.publish("air/temp", String(temp_C2));
    client.publish("water/temp", String(temp_C1));
    if (temp_C2 > 33){
      Serial.println( temp_C2 );
      digitalWrite(D4, LOW);
    }else if (temp_C2 < 33){
      digitalWrite(D4, HIGH);
    }
  }
  if (pmpi>=ipmp*600){
    pmpi=0;
    attachInterrupt (D7, blink, FALLING);//digitalPinToInterrupt (interruptPin2)
    digitalWrite(D5, LOW);
    pmptime=millis();
    Serial.println("Hi");
  }
  if (onemsg){
    onemsg=false;
    client.publish("pump/live", String(pmptime));
  }
  //  long t = millis();
   //TempLoop( t );
  delay(100);
  tmi++;
  pmpi++;
}

void blink () {
  detachInterrupt (D7);
  digitalWrite(D5, HIGH);
  pmptime=millis()-pmptime;
  onemsg=true;
  //client.publish("pump/live", String(pmptime));
  Serial.println("Interrupt");
}

