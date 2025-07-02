const int potHiz = A0;  // Hız için potansiyometre
const int potYon = A1;  // Yön için potansiyometre

void setup() {
  Serial.begin(9600);
}

void loop() {
  int hizDegeri = analogRead(potHiz);  // 0 - 1023
  int yonDegeri = analogRead(potYon);  // 0 - 1023

  // Hızı 0-100 arası, yönü -90 ila +90 dereceye ölçekle
  int hiz = map(hizDegeri, 0, 1023, 0, 100);         
  int yon = map(yonDegeri, 0, 1023,  0, 360);        

  Serial.print("HIZ:");
  Serial.print(hiz);
  Serial.print(" YON:");
  Serial.println(yon);

  delay(350);  // 100ms'de bir gönder
}
