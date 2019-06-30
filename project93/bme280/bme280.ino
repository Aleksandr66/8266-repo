#include "Wire.h"
#include "Adafruit_Sensor.h"
#include "Adafruit_BME280.h"

const float SEA_LEVEL_PRESSURE_HPA = 1013.25;
const int DELAY = 3000;
const int STARTUP_DELAY = 500;

Adafruit_BME280 bme;

void setup() {
  Serial.begin(115200);
  Wire.begin(D2, D1);
  Wire.setClock(100000);
  if (!bme.begin())
  {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    //while (1)
    //{
    //  yield();
    //  delay(DELAY);
    //}
  }
  delay(STARTUP_DELAY);

}

void loop() {
 float tempC = bme.readTemperature();
 float humidity = bme.readHumidity();
 float pressurePascals = bme.readPressure();

// Print to serial monitor
Serial.println(tempC);
Serial.println(humidity);
Serial.println(pressurePascals/133.321995);
// Display data on screen in metric units
 
 yield();
 delay(DELAY);
}
