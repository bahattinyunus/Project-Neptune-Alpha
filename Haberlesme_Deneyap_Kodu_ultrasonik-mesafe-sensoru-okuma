// KODUN ÖZETİ: Deneyapa bağlı mesafe sensörünün değerleri seri porta yazdırılıyor.
String received_data = "";  // Gelen veriyi tutmak için değişken
#define TRIG_PIN D0
#define ECHO_PIN D1
void setup() {
  Serial.begin(9600);  // Seri haberleşmeyi başlat
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.println("Hazir");
}

void loop() {
  long duration;
  float distance;
  // Trig pinine kısa bir sinyal gönder
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Echo pininden dönen sinyali ölç
  duration = pulseIn(ECHO_PIN, HIGH);

  // Mesafeyi hesapla (cm cinsinden)
  distance = duration * 0.034 / 2;
  Serial.print("Mesafe: ");
  Serial.print(distance);
  Serial.println(" cm");
  delay(500);

}
