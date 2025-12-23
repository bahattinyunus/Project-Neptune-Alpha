#include <ESP32Servo.h>

/*
 * ROV TACTICAL FIRMWARE v2.1
 * Hybrid Control: Serial Autonomous Command Parser + 8-Motor Pro-Mixing
 */

#define MAX_VAL 1940
#define MIN_VAL 1060
#define CENTER_VAL 1500
#define BAUD_RATE 115200

// Servo objects for 8 motors
Servo motor[8];
int pins[8] = {D1, D2, D3, D4, D5, D6, D7, D8};

// Axis values (from Serial)
int axisX1 = CENTER_VAL; // Rotation / Turn
int axisY1 = CENTER_VAL; // Forward / Backward
int axisX2 = CENTER_VAL; // Strafe / Lateral
int axisY2 = CENTER_VAL; // Vertical / Depth

unsigned long lastSerialTime = 0;
const int safetyTimeout = 2000;

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.println(">>> ROV TACTICAL SYSTEM v2.1 ONLINE");
  
  for(int i=0; i<8; i++){
    motor[i].attach(pins[i]);
    motor[i].writeMicroseconds(CENTER_VAL);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    parseCommands(input);
    lastSerialTime = millis();
  }

  // Safety Fail-safe
  if (millis() - lastSerialTime > safetyTimeout) {
    axisX1 = axisY1 = axisX2 = axisY2 = CENTER_VAL;
  }

  calculateAndDrive();
  delay(20);
}

void parseCommands(String data) {
  // Expected Format: X1:1500,Y1:1500,X2:1500,Y2:1500
  int x1Idx = data.indexOf("X1:");
  int y1Idx = data.indexOf("Y1:");
  int x2Idx = data.indexOf("X2:");
  int y2Idx = data.indexOf("Y2:");

  if (x1Idx != -1 && y1Idx != -1 && x2Idx != -1 && y2Idx != -1) {
    axisX1 = data.substring(x1Idx + 3, data.indexOf(",", x1Idx)).toInt();
    axisY1 = data.substring(y1Idx + 3, data.indexOf(",", y1Idx)).toInt();
    axisX2 = data.substring(x2Idx + 3, data.indexOf(",", x2Idx)).toInt();
    axisY2 = data.substring(y2Idx + 3).toInt();
    
    axisX1 = constrain(axisX1, MIN_VAL, MAX_VAL);
    axisY1 = constrain(axisY1, MIN_VAL, MAX_VAL);
    axisX2 = constrain(axisX2, MIN_VAL, MAX_VAL);
    axisY2 = constrain(axisY2, MIN_VAL, MAX_VAL);
  }
}

void calculateAndDrive() {
  // 8-Motor Professional Mixing Logic
  // M1-M4: Horizontal (XY Movement + Yaw)
  // M5-M8: Vertical (Z Movement + Pitch/Roll)
  
  int x1 = axisX1 - CENTER_VAL;
  int y1 = axisY1 - CENTER_VAL;
  int x2 = axisX2 - CENTER_VAL;
  int y2 = axisY2 - CENTER_VAL;

  // Horizontal Thrusters (Square Configuration)
  int m1 = CENTER_VAL - x1 - x2 + y1; // Front Right
  int m2 = CENTER_VAL + x1 + x2 + y1; // Front Left
  int m3 = CENTER_VAL - x1 + x2 - y1; // Rear Left
  int m4 = CENTER_VAL + x1 - x2 - y1; // Rear Right

  // Vertical Thrusters
  int m5 = CENTER_VAL + y2; // Front Right Vertical
  int m6 = CENTER_VAL + y2; // Front Left Vertical
  int m7 = CENTER_VAL + y2; // Rear Left Vertical
  int m8 = CENTER_VAL + y2; // Rear Right Vertical

  // Apply to motors
  motor[0].writeMicroseconds(constrain(m1, MIN_VAL, MAX_VAL));
  motor[1].writeMicroseconds(constrain(m2, MIN_VAL, MAX_VAL));
  motor[2].writeMicroseconds(constrain(m3, MIN_VAL, MAX_VAL));
  motor[3].writeMicroseconds(constrain(m4, MIN_VAL, MAX_VAL));
  motor[4].writeMicroseconds(constrain(m5, MIN_VAL, MAX_VAL));
  motor[5].writeMicroseconds(constrain(m6, MIN_VAL, MAX_VAL));
  motor[6].writeMicroseconds(constrain(m7, MIN_VAL, MAX_VAL));
  motor[7].writeMicroseconds(constrain(m8, MIN_VAL, MAX_VAL));
}