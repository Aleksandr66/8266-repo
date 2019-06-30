/*!
 * @file DFRobot_VL53L0X.ino
 * @brief DFRobot's Laser rangefinder library
 * @n The example shows the usage of VL53L0X in a simple way.

 * @copyright	[DFRobot](http://www.dfrobot.com), 2016
 * @copyright	GNU Lesser General Public License
 
 * @author [LiXin]
 * @version  V1.0
 * @date  2017-8-21
 * @https://github.com/DFRobot/DFRobot_VL53L0X
 timer*/
#include "Arduino.h"
#include "Wire.h"
#include "DFRobot_VL53L0X.h"


float lmin = 350;
float lmax = 30;
float litre = 30;
/*****************Keywords instruction*****************/
//Continuous--->Continuous measurement model
//Single------->Single measurement mode
//High--------->Accuracy of 0.25 mm
//Low---------->Accuracy of 1 mm
/*****************Function instruction*****************/
//setMode(ModeSta te mode, PrecisionState precision)
  //*This function is used to set the VL53L0X mode
  //*mode: Set measurement mode       Continuous or Single
  //*precision: Set the precision     High or Low
//void start()
  //*This function is used to enabled VL53L0X
//float getDistance()
  //*This function is used to get the distance
//uint16_t getAmbientCount()
  //*This function is used to get the ambient count
//uint16_t getSignalCount()
  //*This function is used to get the signal count
//uint8_t getStatus();
  //*This function is used to get the status
//void stop()
  //*This function is used to stop measuring

DFRobotVL53L0X sensor;


void setup() {
  //initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  //join i2c bus (address optional for master)
  Wire.begin(D6,D7);
  //Set I2C sub-device address
  sensor.begin(0x50);
  //Set to Back-to-back mode and high precision mode
  sensor.setMode(Single,High);
  //Laser rangefinder begins to work
  sensor.start();
}

void loop() 
{
  
  //Get the distance
  Serial.print("Distance: ");Serial.println(String(Volume()));
  //The delay is added to demonstrate the effect, and if you do not add the delay,
  //it will not affect the measurement accuracy
}

float Volume() {
  
  float ml;
  float lastdist;
  float distance = 0;
  int z;
  for (int i = 0; i < 5; i++) {
    sensor.start();
    distance += sensor.getDistance();
    delay(200);
    z++;
    sensor.stop();
  }
  distance /= z;
  if (distance < 16000) {
    if (abs(lastdist - distance) >= 10) {
      lastdist = distance;
    }
  } else {
    //msgsms("Датчик емкости неисправен");
  }
  ml = (lmin - lastdist) / ((lmin - lmax) / litre);
  
  return ml;
}
