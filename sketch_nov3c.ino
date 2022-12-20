#define led_pin 6

void setup() {
  Serial.begin(9600);
  while (!Serial){
    
  }
  pinMode(led_pin, OUTPUT);
}

void loop() {
  while (Serial.available() > 0){ //если что-то отправлено
    char message = Serial.read(); //считываем сообщение из др комп
    Serial.println(message);
    switch(message) {
      case '1': //ззажигаем лампочку
        digitalWrite(led_pin, HIGH);
      break;
      case '0': //выключаем лампочку
        digitalWrite(led_pin, LOW);
      break;
    }
  }
}

