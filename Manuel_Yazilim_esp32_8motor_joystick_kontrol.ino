#include <ESP32Servo.h>

#define maxdeger 1940 //max 2000 oluyor escler 1000-2000 arası calisir
#define mindeger 1060

float valueJoyStick_X_1 = A0;
float valueJoyStick_Y_1 = A2;
float valueJoyStick_X_2 = A1;
float valueJoyStick_Y_2 = A3;
int buton1 = 0;
int buton2 = 0;
float hizBoleni = 1.0;
int sabitleme_toleransi = 60;

//Motorları tersine çevirmek için örnek 
//#define TERSONSOLUST

Servo onsagalt,onsolalt,onsolust,onsagust,arsagalt,arsagust,arsolalt,arsolust;
int onsagalt_deger, onsolalt_deger, arsagalt_deger, arsolalt_deger,onsagust_deger, onsolust_deger, arsagust_deger, arsolust_deger;

void setup () {
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

void loop () {
valueJoyStick_X_1 = analogRead(A0)/4+1000;
valueJoyStick_Y_1 = analogRead(A2)/4+1000;
valueJoyStick_X_2 = analogRead(A1)/4+1000;
valueJoyStick_Y_2 = analogRead(A3)/4+1000;

// valueJoyStick_X_1 = analogRead(A0);
// valueJoyStick_Y_1 = analogRead(A2);
// valueJoyStick_X_2 = analogRead(A1);
// valueJoyStick_Y_2 = analogRead(A3);

// valueJoyStick_X_1 = map(valueJoyStick_X_1,0,4095,1060,1940);
// valueJoyStick_Y_1 = map(valueJoyStick_Y_1,0,4095,1060,1940);
// valueJoyStick_X_2 = map(valueJoyStick_X_2,0,4095,1060,1940);
// valueJoyStick_Y_2 = map(valueJoyStick_Y_2,0,4095,1060,1940);


//Joystick değerlerini merkezi değiştirmeden bölme işlemleri
valueJoyStick_X_1 = 1500 + (valueJoyStick_X_1 - 1500) / hizBoleni;
valueJoyStick_Y_1 = 1500 + (valueJoyStick_Y_1 - 1500) / hizBoleni;
valueJoyStick_X_2 = 1500 + (valueJoyStick_X_2 - 1500) / hizBoleni;
valueJoyStick_Y_2 = 1500 + (valueJoyStick_Y_2 - 1500) / hizBoleni;

if (valueJoyStick_X_1 > maxdeger) valueJoyStick_X_1 = maxdeger; 
if (valueJoyStick_Y_1 > maxdeger) valueJoyStick_Y_1 = maxdeger;
if (valueJoyStick_X_2 > maxdeger) valueJoyStick_X_2 = maxdeger;
if (valueJoyStick_Y_2 > maxdeger) valueJoyStick_Y_2 = maxdeger;
    
if (valueJoyStick_X_1 < mindeger) valueJoyStick_X_1 = mindeger;
if (valueJoyStick_Y_1 < mindeger)valueJoyStick_Y_1 = mindeger;
if (valueJoyStick_X_2 < mindeger) valueJoyStick_X_2 = mindeger;
if (valueJoyStick_Y_2 < mindeger)valueJoyStick_Y_2 = mindeger;

// if (valueJoyStick_X_1 < 1500 + sabitleme_toleransi / hizBoleni && valueJoyStick_X_1 > 1500 - sabitleme_toleransi / hizBoleni)
//         valueJoyStick_X_1 = 1500;
// if (valueJoyStick_Y_1 < 1500 + sabitleme_toleransi / hizBoleni && valueJoyStick_Y_1 > 1500 - sabitleme_toleransi / hizBoleni)
//         valueJoyStick_Y_1 = 1500;
// if (valueJoyStick_X_2 < 1500 + sabitleme_toleransi / hizBoleni && valueJoyStick_X_2 > 1500 - sabitleme_toleransi / hizBoleni)
//         valueJoyStick_X_2 = 1500;
// if (valueJoyStick_Y_2 < 1500 + sabitleme_toleransi / hizBoleni && valueJoyStick_Y_2 > 1500 - sabitleme_toleransi / hizBoleni)
//         valueJoyStick_Y_2 = 1500;

Serial.print("X1 ");
Serial.print(valueJoyStick_X_1);
Serial.print("  ");
Serial.print("Y1 ");
Serial.print(valueJoyStick_Y_1);
Serial.print("  ");
Serial.print("X2 ");
Serial.print(valueJoyStick_X_2);
Serial.print("  ");
Serial.print("Y2 ");
Serial.print(valueJoyStick_Y_2);
Serial.print("     ");

onsagust_deger = 1500 - (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
onsolust_deger = 1500 + (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
arsolust_deger = 1500 - (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
arsagust_deger = 1500 + (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) + (valueJoyStick_Y_1 - 1500);
onsagalt_deger = 1500 - (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);
onsolalt_deger = 1500 + (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) + (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);
arsolalt_deger = 1500 - (valueJoyStick_X_1 - 1500) + (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);
arsagalt_deger = 1500 + (valueJoyStick_X_1 - 1500) - (valueJoyStick_X_2 - 1500) - (valueJoyStick_Y_2 - 1500) - (valueJoyStick_Y_1 - 1500);

// Ters Motor Müdahalesi
// #ifdef TERSONSOLUST
//   onsolust_deger=3000-onsolust_deger;
// #endif

onsagalt.writeMicroseconds(onsagalt_deger);
onsolalt.writeMicroseconds(onsolalt_deger);
onsolust.writeMicroseconds(onsolust_deger);
onsagust.writeMicroseconds(onsagust_deger);
arsagalt.writeMicroseconds(arsagalt_deger);
arsagust.writeMicroseconds(arsagust_deger);
arsolalt.writeMicroseconds(arsolalt_deger);
arsolust.writeMicroseconds(arsolust_deger);
//delay(10);

Serial.print("M1: ");
Serial.print(onsagust_deger);
Serial.print("  ");
Serial.print("M2: ");
Serial.print(onsolust_deger);
Serial.print("  ");
Serial.print("M3: ");
Serial.print(arsolust_deger);
Serial.print("  ");
Serial.print("M4: ");
Serial.print(arsagust_deger);
Serial.print("  ");
Serial.print("M5: ");
Serial.print(onsagalt_deger);
Serial.print("  ");
Serial.print("M6: ");
Serial.print(onsolalt_deger);
Serial.print("  ");
Serial.print("M7: ");
Serial.print(arsolalt_deger);
Serial.print("  ");
Serial.print("M8: ");
Serial.print(arsagalt_deger);
Serial.println("  ");
delay(20);
}