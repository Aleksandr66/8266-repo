void setup() {
Serial.begin(115200);
pinMode(D7, INPUT_PULLUP);
attachInterrupt(D7, doSth, FALLING);
}

void loop() {
Serial.println(digitalRead(D7));
delay(1000);
}

void doSth() {
Serial.println("Check!");
}
