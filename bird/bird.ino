const int buttonPin = 52;     // the number of the pushbutton pin
const int ledPin =  22;      // the number of the LED pin

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status

void setup() {
  Serial.begin(19200);
  Serial.setTimeout(5);
  
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin,  INPUT_PULLUP);
  digitalWrite(ledPin, LOW);
}

unsigned long downtime = 0;
char buffer[100];

void loop() {
  if (Serial.available() > 0 && downtime == 0) {
    Serial.readBytes(buffer, 100); 
    digitalWrite(ledPin, HIGH);
    downtime = millis();
  }
  
  if (downtime > 0 && (millis() - downtime) > 200){
    digitalWrite(ledPin, LOW);
    downtime = 0;
  }

  
//  buttonState = digitalRead(buttonPin);
//  if (buttonState == HIGH) {
//    digitalWrite(ledPin, LOW);
//  }
//  else {
//    digitalWrite(ledPin, HIGH);
//  }
}
