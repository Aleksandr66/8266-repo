#include <Wire.h>
#include "RTClib.h"

RTC_DS3231 rtc;

char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

#include <ESP8266WiFi.h>
#include <TimeLib.h>

TimeLib tl(5); // Например: TimeLib tt(2); - Калининград.
// Зона по умолчанию - 3 (Москва)

void InitWiFi()
{
  const char * WiFi_Name = "Xiaomi";
  const char * WiFi_Pass = "891261AA";
  WiFi.begin( WiFi_Name, WiFi_Pass );
  while (WiFi.waitForConnectResult() != WL_CONNECTED) WiFi.begin( WiFi_Name, WiFi_Pass );
}

void setup () {

#ifndef ESP8266
  while (!Serial); // for Leonardo/Micro/Zero
#endif

  Serial.begin(115200);
  Wire.begin(D2, D1);
  delay(3000); // wait for console opening

  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
    InitWiFi();
  }

  if (rtc.lostPower()) {
    Serial.println("RTC lost power, lets set the time!");
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    //rtc.adjust(DateTime(2019, 5, 11, 18, 57, 0));
  }
}

void loop () {
  String timer = tl.tmTime();
  String H, M, S;
  H = timer.substring(0, timer.indexOf(":"));
  M = timer.substring(timer.indexOf(":") + 1, timer.lastIndexOf(":"));
  S = timer.substring(timer.lastIndexOf(":") + 1, timer.length());
  DateTime now = rtc.now();
  rtc.adjust(DateTime(2019, 5, 11, H.toInt(), M.toInt(), S.toInt()));
  Serial.print(now.year(), DEC);
  Serial.print('/');
  Serial.print(now.month(), DEC);
  Serial.print('/');
  Serial.print(now.day(), DEC);
  Serial.print(" (");
  Serial.print(daysOfTheWeek[now.dayOfTheWeek()]);
  Serial.print(") ");
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.print(now.second(), DEC);
  Serial.println();

  Serial.print(" since midnight 1/1/1970 = ");
  Serial.print(now.unixtime());
  Serial.print("s = ");
  Serial.print(now.unixtime() / 86400L);
  Serial.println("d");

  // calculate a date which is 7 days and 30 seconds into the future
  DateTime future (now + TimeSpan(7, 12, 30, 6));

  Serial.print(" now + 7d + 30s: ");
  Serial.print(future.year(), DEC);
  Serial.print('/');
  Serial.print(future.month(), DEC);
  Serial.print('/');
  Serial.print(future.day(), DEC);
  Serial.print(' ');
  Serial.print(future.hour(), DEC);
  Serial.print(':');
  Serial.print(future.minute(), DEC);
  Serial.print(':');
  Serial.print(future.second(), DEC);
  Serial.println();

  Serial.println();
  delay(1000);
}
