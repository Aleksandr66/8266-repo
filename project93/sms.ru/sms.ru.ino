#include <TimeLib.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

TimeLib tt(5);

const char ssid[] = "Xiaomi";  //  SSID (название) вашей сети
const char pass[] = "891261AA";       // пароль к вашей сети
const int httpPort = 80;
String host = "http://sms.ru";
String sms_id = "E41A545D-870B-7733-3ADC-ABA1D647A0FB";
String tel = "9995635420";
int count = 0;
int interval = 0;
int inter = 0;
int outer = 0;
int mils;
int msg = 1;
String state;
void setup() {

  Serial.begin(115200);
  
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.print("Start");
}

void loop() {
  if (msg == 1) {
    msg = 0;
    msgg("Ха ЬЬ херакс");
  }
}


void msgg(String message) {
  HTTPClient http;
  message.replace(" ", "+");
  String url = "/sms/send?";
  url += "api_id=";
  url += sms_id;
  url += "&to=7";
  url += tel;
  url += "&msg=";
  url += message;
  String Link = host + url;
  http.begin(Link);     //Specify request destination

  int httpCode = http.GET();
  if (httpCode == HTTP_CODE_OK)
  {
    Serial.print("HTTP response code ");
    Serial.println(httpCode);
    String response = http.getString();
    Serial.println(response);

  }
  else
  {
    Serial.println("Error in HTTP request");
  }

  http.end();
}

