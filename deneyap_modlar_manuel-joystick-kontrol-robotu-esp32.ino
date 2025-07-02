#include <ESP32Servo.h>

#define maxdeger 1940
#define mindeger 1060

float hizBoleni = 1.0;

Servo onsagalt, onsolalt, onsolust, onsagust, arsagalt, arsagust, arsolalt, arsolust;
int onsagalt_deger, onsolalt_deger, arsagalt_deger, arsolalt_deger;
int onsagust_deger, onsolust_deger, arsagust_deger, arsolust_deger;

void setup() {
  Serial.begin(9600);
  Serial.println("AKINTAY MANUEL SÜRÜŞ MODU AKTİF");
  Serial.println("............Başlıyor..............");

  onsagust.attach(D1);
  onsolust.attach(D2);
  arsolust.attach(D3);
  arsagust.attach(D4);
  onsagalt.attach(D5);
  onsolalt.attach(D6);
  arsolalt.attach(D7);
  arsagalt.attach(D8);

  pinMode(D9, OUTPUT);
  pinMode(D0, OUTPUT);
}

void loop() {
  mod1();  // Tüm işlemler burada
}

void mod1() {
  float X1 = analogRead(A0) / 4.0 + 1000;
  float Y1 = analogRead(A2) / 4.0 + 1000;
  float X2 = analogRead(A1) / 4.0 + 1000;
  float Y2 = analogRead(A3) / 4.0 + 1000;

  X1 = 1500 + (X1 - 1500) / hizBoleni;
  Y1 = 1500 + (Y1 - 1500) / hizBoleni;
  X2 = 1500 + (X2 - 1500) / hizBoleni;
  Y2 = 1500 + (Y2 - 1500) / hizBoleni;

  if (X1 > maxdeger) X1 = maxdeger;
  if (Y1 > maxdeger) Y1 = maxdeger;
  if (X2 > maxdeger) X2 = maxdeger;
  if (Y2 > maxdeger) Y2 = maxdeger;

  if (X1 < mindeger) X1 = mindeger;
  if (Y1 < mindeger) Y1 = mindeger;
  if (X2 < mindeger) X2 = mindeger;
  if (Y2 < mindeger) Y2 = mindeger;

  Serial.print("X1 "); Serial.print(X1);
  Serial.print("  Y1 "); Serial.print(Y1);
  Serial.print("  X2 "); Serial.print(X2);
  Serial.print("  Y2 "); Serial.println(Y2);

  onsagust_deger = 1500 - (X1 - 1500) - (X2 - 1500) + (Y2 - 1500) + (Y1 - 1500);
  onsolust_deger = 1500 + (X1 - 1500) + (X2 - 1500) + (Y2 - 1500) + (Y1 - 1500);
  arsolust_deger = 1500 - (X1 - 1500) + (X2 - 1500) - (Y2 - 1500) + (Y1 - 1500);
  arsagust_deger = 1500 + (X1 - 1500) - (X2 - 1500) - (Y2 - 1500) + (Y1 - 1500);
  onsagalt_deger = 1500 - (X1 - 1500) - (X2 - 1500) + (Y2 - 1500) - (Y1 - 1500);
  onsolalt_deger = 1500 + (X1 - 1500) + (X2 - 1500) + (Y2 - 1500) - (Y1 - 1500);
  arsolalt_deger = 1500 - (X1 - 1500) + (X2 - 1500) - (Y2 - 1500) - (Y1 - 1500);
  arsagalt_deger = 1500 + (X1 - 1500) - (X2 - 1500) - (Y2 - 1500) - (Y1 - 1500);

  onsagalt.writeMicroseconds(onsagalt_deger);
  onsolalt.writeMicroseconds(onsolalt_deger);
  onsolust.writeMicroseconds(onsolust_deger);
  onsagust.writeMicroseconds(onsagust_deger);
  arsagalt.writeMicroseconds(arsagalt_deger);
  arsagust.writeMicroseconds(arsagust_deger);
  arsolalt.writeMicroseconds(arsolalt_deger);
  arsolust.writeMicroseconds(arsolust_deger);

  Serial.print("M1: "); Serial.print(onsagust_deger); Serial.print("  ");
  Serial.print("M2: "); Serial.print(onsolust_deger); Serial.print("  ");
  Serial.print("M3: "); Serial.print(arsolust_deger); Serial.print("  ");
  Serial.print("M4: "); Serial.print(arsagust_deger); Serial.print("  ");
  Serial.print("M5: "); Serial.print(onsagalt_deger); Serial.print("  ");
  Serial.print("M6: "); Serial.print(onsolalt_deger); Serial.print("  ");
  Serial.print("M7: "); Serial.print(arsolalt_deger); Serial.print("  ");
  Serial.print("M8: "); Serial.println(arsagalt_deger);
}

void mod2() {
  float X1 = analogRead(A0) / 4.0 + 1000;
  float Y2 = analogRead(A3) / 4.0 + 1000;

  X1 = 1500 + (X1 - 1500) / hizBoleni;
  Y2 = 1500 + (Y2 - 1500) / hizBoleni;

  if (X1 > maxdeger) X1 = maxdeger;
  if (Y2 > maxdeger) Y2 = maxdeger;

  if (X1 < mindeger) X1 = mindeger;
  if (Y2 < mindeger) Y2 = mindeger;

  Serial.print("X1: "); Serial.print(X1);
  Serial.print("  Y2: "); Serial.println(Y2);

  onsagust_deger = 1500 - (X1 - 1500) + (Y2 - 1500);
  onsolust_deger = 1500 + (X1 - 1500) + (Y2 - 1500);
  arsolust_deger = 1500 - (X1 - 1500) - (Y2 - 1500);
  arsagust_deger = 1500 + (X1 - 1500) - (Y2 - 1500);
  onsagalt_deger = 1500 - (X1 - 1500) + (Y2 - 1500);
  onsolalt_deger = 1500 + (X1 - 1500) + (Y2 - 1500);
  arsolalt_deger = 1500 - (X1 - 1500) - (Y2 - 1500);
  arsagalt_deger = 1500 + (X1 - 1500) - (Y2 - 1500);

  onsagalt.writeMicroseconds(onsagalt_deger);
  onsolalt.writeMicroseconds(onsolalt_deger);
  onsolust.writeMicroseconds(onsolust_deger);
  onsagust.writeMicroseconds(onsagust_deger);
  arsagalt.writeMicroseconds(arsagalt_deger);
  arsagust.writeMicroseconds(arsagust_deger);
  arsolalt.writeMicroseconds(arsolalt_deger);
  arsolust.writeMicroseconds(arsolust_deger);

  Serial.print("M1: "); Serial.print(onsagust_deger); Serial.print("  ");
  Serial.print("M2: "); Serial.print(onsolust_deger); Serial.print("  ");
  Serial.print("M3: "); Serial.print(arsolust_deger); Serial.print("  ");
  Serial.print("M4: "); Serial.print(arsagust_deger); Serial.print("  ");
  Serial.print("M5: "); Serial.print(onsagalt_deger); Serial.print("  ");
  Serial.print("M6: "); Serial.print(onsolalt_deger); Serial.print("  ");
  Serial.print("M7: "); Serial.print(arsolalt_deger); Serial.print("  ");
  Serial.print("M8: "); Serial.println(arsagalt_deger);
}


