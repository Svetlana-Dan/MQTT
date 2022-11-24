#define led_pin A2
int count=0;

void setup()
{
  Serial.begin(9600);
  pinMode(led_pin, INPUT);
}

void loop()
{
  int val = analogRead(led_pin);
  val = map(val, 0, 1023, 0, 100);
  delay(100);
  Serial.print(val);
}

