#include <ESP32Servo.h>

#define maxdeger 1940
#define mindeger 1060

float valueJoyStick_X_1 = 1500;
float valueJoyStick_Y_1 = 1500;
float valueJoyStick_X_2 = 1500;
float valueJoyStick_Y_2 = 1500;
float hizBoleni = 1.0;

Servo onsagalt, onsolalt, onsolust, onsagust, arsagalt, arsagust, arsolalt, arsolust;
int onsagalt_deger, onsolalt_deger, arsagalt_deger, arsolalt_deger;
int onsagust_deger, onsolust_deger, arsagust_deger, arsolust_deger;

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 MOTOR KONTROLÜ BAŞLADI");

  onsagust.attach(D1); onsolust.attach(D2);
  arsolust.attach(D3); arsagust.attach(D4);
  onsagalt.attach(D5); onsolalt.attach(D6);
  arsolalt.attach(D7); arsagalt.attach(D8);
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();  // boşlukları temizle

    int x1_index = data.indexOf("X1:");
    int y1_index = data.indexOf("Y1:");
    int x2_index = data.indexOf("X2:");
    int y2_index = data.indexOf("Y2:");

    if (x1_index != -1 && y1_index != -1 && x2_index != -1 && y2_index != -1) {
      valueJoyStick_X_1 = data.substring(x1_index + 3, data.indexOf(',', x1_index)).toInt();
      valueJoyStick_Y_1 = data.substring(y1_index + 3, data.indexOf(',', y1_index)).toInt();
      valueJoyStick_X_2 = data.substring(x2_index + 3, data.indexOf(',', x2_index)).toInt();
      valueJoyStick_Y_2 = data.substring(y2_index + 3).toInt();
    }
  }

  // Girişleri yumuşat
  valueJoyStick_X_1 = 1500 + (valueJoyStick_X_1 - 1500) / hizBoleni;
  valueJoyStick_Y_1 = 1500 + (valueJoyStick_Y_1 - 1500) / hizBoleni;
  valueJoyStick_X_2 = 1500 + (valueJoyStick_X_2 - 1500) / hizBoleni;
  valueJoyStick_Y_2 = 1500 + (valueJoyStick_Y_2 - 1500) / hizBoleni;

  // Limitler
  valueJoyStick_X_1 = constrain(valueJoyStick_X_1, mindeger, maxdeger);
  valueJoyStick_Y_1 = constrain(valueJoyStick_Y_1, mindeger, maxdeger);
  valueJoyStick_X_2 = constrain(valueJoyStick_X_2, mindeger, maxdeger);
  valueJoyStick_Y_2 = constrain(valueJoyStick_Y_2, mindeger, maxdeger);

  // MOTOR PWM HESAPLARI (dokunulmadı!)
  onsagust_deger = 1500 - (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
  onsolust_deger = 1500 + (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
  arsolust_deger = 1500 - (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
  arsagust_deger = 1500 + (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
  onsagalt_deger = 1500 - (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);
  onsolalt_deger = 1500 + (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);
  arsolalt_deger = 1500 - (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);
  arsagalt_deger = 1500 + (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);

  // Motorlara gönder
  onsagalt.writeMicroseconds(onsagalt_deger);
  onsolalt.writeMicroseconds(onsolalt_deger);
  onsolust.writeMicroseconds(onsolust_deger);
  onsagust.writeMicroseconds(onsagust_deger);
  arsagalt.writeMicroseconds(arsagalt_deger);
  arsagust.writeMicroseconds(arsagust_deger);
  arsolalt.writeMicroseconds(arsolalt_deger);
  arsolust.writeMicroseconds(arsolust_deger);

  // Python'a değerleri gönder
  Serial.print("M1:"); Serial.print(onsagust_deger); Serial.print(",");
  Serial.print("M2:"); Serial.print(onsolust_deger); Serial.print(",");
  Serial.print("M3:"); Serial.print(arsolust_deger); Serial.print(",");
  Serial.print("M4:"); Serial.print(arsagust_deger); Serial.print(",");
  Serial.print("M5:"); Serial.print(onsagalt_deger); Serial.print(",");
  Serial.print("M6:"); Serial.print(onsolalt_deger); Serial.print(",");
  Serial.print("M7:"); Serial.print(arsolalt_deger); Serial.print(",");
  Serial.print("M8:"); Serial.println(arsagalt_deger);

  delay(20);  // stabil çalışsın
}
