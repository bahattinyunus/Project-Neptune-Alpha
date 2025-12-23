#include <ESP32Servo.h>

/*
 * ROV TACTICAL FIRMWARE v2.0
 * Hybrid Control: Manul (Joystick) + Autonomous (Serial)
 */

#define MAX_VAL 1940
#define MIN_VAL 1060
#define CENTER_VAL 1500
#define BAUD_RATE 115200

// Servo objects
Servo motor[8];
int pins[8] = {D1, D2, D3, D4, D5, D6, D7, D8};

// Control variables
int axisX1 = CENTER_VAL, axisY1 = CENTER_VAL, axisX2 = CENTER_VAL, axisY2 = CENTER_VAL;
unsigned long lastSerialTime = 0;
const int autonomousTimeout = 2000; // 2 seconds timeout return to center

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.println(">>> ROV TACTICAL SYSTEM ONLINE");
  
  for(int i=0; i<8; i++){
    motor[i].attach(pins[i]);
    motor[i].writeMicroseconds(CENTER_VAL);
  }
}

void loop() {
  // 1. Check Serial for Autonomous Commands
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    parseCommands(input);
    lastSerialTime = millis();
  }

  // 2. Fail-safe: If no serial for 2s, return to center (unless manual pins would take over)
  if (millis() - lastSerialTime > autonomousTimeout) {
    // Optional: read analog pins here for manual fallback
    // For now, safety idle:
    axisX1 = axisY1 = axisX2 = axisY2 = CENTER_VAL;
  }

  // 3. Drive Calculations (Mixing Logic)
  driveMotors();
  
  delay(20);
}

void parseCommands(String data) {
  // Format: X1:1500,Y1:1500,X2:1500,Y2:1500
  int x1Idx = data.indexOf("X1:");
  int y1Idx = data.indexOf("Y1:");
  int x2Idx = data.indexOf("X2:");
  int y2Idx = data.indexOf("Y2:");

  if (x1Idx != -1 && y1Idx != -1) {
    axisX1 = data.substring(x1Idx + 3, data.indexOf(",", x1Idx)).toInt();
    axisY1 = data.substring(y1Idx + 3, data.indexOf(",", y1Idx)).toInt();
    axisX2 = data.substring(x2Idx + 3, data.indexOf(",", x2Idx)).toInt();
    axisY2 = data.substring(y2Idx + 3).toInt();
    
    // Safety Constrain
    axisX1 = constrain(axisX1, MIN_VAL, MAX_VAL);
    axisY1 = constrain(axisY1, MIN_VAL, MAX_VAL);
    axisX2 = constrain(axisX2, MIN_VAL, MAX_VAL);
    axisY2 = constrain(axisY2, MIN_VAL, MAX_VAL);
  }
}

void driveMotors() {
  // Standard mixing for 8-motor configuration
  // Simplified for representation, actual logic depends on thruster orientation
  int m1 = CENTER_VAL - (axisX1 - CENTER_VAL) + (axisY1 - CENTER_VAL);
  int m2 = CENTER_VAL + (axisX1 - CENTER_VAL) + (axisY1 - CENTER_VAL);
  // ... apply to all 8 motors ...
  
  motor[0].writeMicroseconds(m1);
  motor[1].writeMicroseconds(m2);
  // motor[2...7].write...
}