#include <ESP32Servo.h>
#include <Wire.h>
#include <LSM6DSL.h>  // Deneyap Kart dahili IMU için

#define mindeger 1060
#define maxdeger 1940

Servo motor[8];
LSM6DSL IMU;

// Setpoint değerleri (ideal yatay pozisyon)
float rollSetpoint = 0.0;
float pitchSetpoint = 0.0;

// IMU’dan alınan verilerle hesaplanan açılar
float actualRoll = 0.0;
float actualPitch = 0.0;

// PID parametreleri
float Kp = 2.0, Ki = 0.0, Kd = 0.5;
float rollError, pitchError;
float rollIntegral = 0, pitchIntegral = 0;
float rollLastError = 0, pitchLastError = 0;
unsigned long lastTime = 0;

// Motor kazançları (45° → sin(45°) = cos(45°) ≈ 0.7071)
const float k45 = 0.7071;

float rollGain[8] = {
  -k45, k45,  k45, -k45,  // Üst motorlar
  -k45, k45,  k45, -k45   // Alt motorlar
};

float pitchGain[8] = {
   k45, k45, -k45, -k45,  // Üst motorlar
   k45, k45, -k45, -k45   // Alt motorlar
};

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!IMU.begin()) {
    Serial.println("IMU başlatılamadı. Lütfen bağlantıyı kontrol edin.");
    while (1); // Sonsuz döngüde kilitlen
  }

  // Motorları D1–D8 pinlerine bağla
  for (int i = 0; i < 8; i++) {
    motor[i].attach(D1 + i); // D1 ~ D8
  }

  lastTime = millis();

  Serial.println("45° eğimli motorlarla PID stabilizasyon başladı...");
}

void loop() {
  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;

  float gyroX, gyroY;
  
  // IMU'dan gyro verilerini oku
  if (IMU.readGyroscope(gyroX, gyroY, nullptr)) {
    // IMU değerlerini entegre ederek açıya çevir
    actualPitch += gyroX * dt;
    actualRoll  += gyroY * dt;

    // PID hesaplaması
    pitchError = pitchSetpoint - actualPitch;
    rollError  = rollSetpoint  - actualRoll;

    pitchIntegral += pitchError * dt;
    rollIntegral  += rollError  * dt;

    float pitchDerivative = (pitchError - pitchLastError) / dt;
    float rollDerivative  = (rollError  - rollLastError)  / dt;

    float pitchOutput = Kp * pitchError + Ki * pitchIntegral + Kd * pitchDerivative;
    float rollOutput  = Kp * rollError  + Ki * rollIntegral  + Kd * rollDerivative;

    pitchLastError = pitchError;
    rollLastError  = rollError;

    // Motorlara sinyal gönderimi
    for (int i = 0; i < 8; i++) {
      int pwm = 1500;
      pwm += pitchOutput * pitchGain[i];
      pwm += rollOutput  * rollGain[i];
      pwm = constrain(pwm, mindeger, maxdeger);
      motor[i].writeMicroseconds(pwm);
    }

    // Debug çıktısı
    Serial.print("Roll: "); Serial.print(actualRoll, 2);
    Serial.print(" | Pitch: "); Serial.print(actualPitch, 2);
    Serial.print(" | R_out: "); Serial.print(rollOutput, 2);
    Serial.print(" | P_out: "); Serial.println(pitchOutput, 2);
  }

  delay(10); // 100 Hz frekans
}

