#include <Wire.h>
#include <Adafruit_LSM6DS.h>
#include <ESP32Servo.h>

#define NUM_MOTORS 8
Servo motors[NUM_MOTORS];
int motorPins[NUM_MOTORS] = {2, 4, 5, 12, 13, 14, 15, 16};

Adafruit_LSM6DS imu;

int x1_joy = 1500;

// PID parametreleri
float Kp = 2.0, Ki = 0.0, Kd = 1.2;
float pid_error = 0, previous_error = 0, integral = 0;
float targetYaw = 0.0;
unsigned long lastTime = 0;

// TEST_MODU aktif ise motor sürme, sadece PWM değerini seri yazdır
#define TEST_MODE true

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!imu.begin_I2C()) {
    Serial.println("IMU başlatılamadı! Bağlantıyı kontrol et.");
    while (1);
  }

  if (!TEST_MODE) {
    for (int i = 0; i < NUM_MOTORS; i++) {
      motors[i].attach(motorPins[i]);
      motors[i].writeMicroseconds(1500);
    }
  } else {
    Serial.println(">>> TEST MODU AKTIF - Motorlar sürülmüyor");
  }

  lastTime = millis();
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    parseJoystick(line);
  }

  sensors_event_t gyroEvent;
  imu.getEvent(NULL, &gyroEvent, NULL);

  float currentYaw = gyroEvent.gyro.z;

  unsigned long currentTime = millis();
  float deltaTime = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;

  pid_error = targetYaw - currentYaw;
  integral += pid_error * deltaTime;
  float derivative = (pid_error - previous_error) / deltaTime;
  previous_error = pid_error;

  float output = Kp * pid_error + Ki * integral + Kd * derivative;
  output = constrain(output, -200, 200);

  for (int i = 0; i < NUM_MOTORS; i++) {
    int pwm = 1500 + output;
    pwm = constrain(pwm, 1100, 1900);

    if (!TEST_MODE) {
      motors[i].writeMicroseconds(pwm);
    } else {
      Serial.print("PWM[");
      Serial.print(i);
      Serial.print("]: ");
      Serial.println(pwm);
    }
  }

  Serial.print("YAW:");
  Serial.print(currentYaw, 2);
  Serial.print(", PID:");
  Serial.print(output);
  Serial.print(", TargetYaw:");
  Serial.println(targetYaw);

  delay(100);
}

void parseJoystick(String line) {
  int x1Index = line.indexOf("X1:");
  int y1Index = line.indexOf("Y1:");
  int x2Index = line.indexOf("X2:");
  int y2Index = line.indexOf("Y2:");

  if (x1Index != -1 && y1Index != -1 && x2Index != -1 && y2Index != -1) {
    x1_joy = line.substring(x1Index + 3, y1Index - 1).toInt();
  }

  targetYaw = map(x1_joy, 1300, 1700, -90, 90);
}