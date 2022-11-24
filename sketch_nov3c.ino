#define led_pin 6

void setup() {
  Serial.begin(9600);
  while (!Serial){
    
  }
  pinMode(led_pin, OUTPUT);
}

void loop() {
  while (Serial.available() > 0){
    char message = Serial.read();
    Serial.println(message);
    switch(message) {
      case '1':
        digitalWrite(led_pin, HIGH);
      break;
      case '0':
        digitalWrite(led_pin, LOW);
      break;
    }
  }
}

