#include <TimeLib.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

TimeLib tt(5);

const char ssid[] = "Xiaomi";  //  SSID (название) вашей сети
const char pass[] = "891261AA";       // пароль к вашей сети
const int httpPort = 80;
const char* host = "http://esp8266-repo.000webhostapp.com";
int count = 0;
int interval = 0;
int inter = 0;
int outer = 0;
int mils;
int msg = 0;
String state;
void setup() {

  Serial.begin(115200);
  pinMode (D7, INPUT_PULLUP);
  pinMode (D5, INPUT_PULLUP);
  attachInterrupt ( D7, In1, FALLING);
  attachInterrupt ( D5, Out1, FALLING);
  Serial.println();
  Serial.println();
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.print("Start");
}

void loop() {
  //msg();
  mils = millis();
  //delay(1000);
  noInterrupts();
  if (msg == 1) {
    msg = 0;
    msgg();
  }
  interrupts();
}

void In1() {
  attachInterrupt ( D5, In2, FALLING);
  attachInterrupt ( D7, Lost, RISING);
}

void In2() {
  attachInterrupt ( D7, In3, RISING);
  attachInterrupt ( D5, In1, RISING);
}

void In3() {
  attachInterrupt ( D5, In, RISING);
  attachInterrupt ( D7, In2, FALLING);
}

void Out1() {
  attachInterrupt ( D7, Out2, FALLING);
  attachInterrupt ( D5, Lost, RISING);
}

void Out2() {
  attachInterrupt ( D5, Out3, RISING);
  attachInterrupt ( D7, Out1, RISING);
}
void Out3() {
  attachInterrupt ( D7, Out, RISING);
  attachInterrupt ( D5, Out2, FALLING);
}

void In() {
  attachInterrupt ( D7, In1, FALLING);
  attachInterrupt ( D5, Out1, FALLING);
  count++;
  inter = millis() - inter;
  //Serial.print(count);
  //Serial.print(" | ");
  //Serial.print(interval/1000);
  //Serial.print("сек | ");
  //Serial.print( tt.tmDate() );
  //Serial.println( tt.tmTime() );
  interval = inter;
  msg = 1;
  state = "in";
  inter = millis();
  //msg();

}

void Out() {
  attachInterrupt ( D7, In1, FALLING);
  attachInterrupt ( D5, Out1, FALLING);
  count--;
  outer = millis() - outer;
  interval = outer;
  state = "out";
  msg = 1;
  outer = millis();
  //Serial.println(count);
}

void Lost() {
  attachInterrupt ( D7, In1, FALLING);
  attachInterrupt ( D5, Out1, FALLING);
  Serial.println("Lost");
}

void msgg() {
  HTTPClient http;
  String url = "/esp.php?";
  url += "id=777";
  url += "&c=";
  url += count;
  url += "&i=";
  url += interval;
  url += "&s=";
  url += state;
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

