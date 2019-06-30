#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>


const char *SERVER_WIFI_SSID = "Xiaomi";
const char *SERVER_WIFI_PASS = "891261AA";



void setupWiFi()
{
   Serial.print("Connecting to WiFi ");
   WiFi.begin(SERVER_WIFI_SSID,SERVER_WIFI_PASS);
   while(WiFi.status() != WL_CONNECTED)
   {
     delay(500);
     Serial.print(".");
   }

   Serial.println("Connected");
}

void setup() {
  Serial.begin(115200);
  setupWiFi();

}

void loop() {
  // put your main code here, to run repeatedly:
  HTTPClient http;

  //Let is try a GET request first
  
  http.begin("http://esp8266-repo.000webhostapp.com/esp.php?id=8877&t=5555&h=1111");

  int httpCode = http.GET();
  if(httpCode == HTTP_CODE_OK)
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


  

  Serial.println();


  delay(3000);

}String url = "/esp.php?";
  url += "id=1000"; 
  url += "&c="; 
  url += count;
  url += "&i="; 
  url += interval;
  url += "&t="; 
  url += tt.tmTime();
  String Link = host + url;
