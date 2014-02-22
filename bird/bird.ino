const int buttonPin = 52;     // the number of the pushbutton pin
const int ledPin =  22;      // the number of the LED pin
const int switchPin =  53;      // the number of the LED pin

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status
int switchState = LOW;

void setup() {
  Serial.begin(19200);
  Serial.setTimeout(5);
  
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin,  INPUT_PULLUP);
  pinMode(switchPin,  INPUT_PULLUP);
  digitalWrite(ledPin, LOW);
  delay(500);
  switchState = digitalRead(switchPin);
}

unsigned long downtime = 0;
char buffer[100];

void loop() {
if (switchState) {
    
  if (Serial.available() > 0 && downtime == 0) {
    Serial.readBytes(buffer, 100); 
    digitalWrite(ledPin, HIGH);
    downtime = millis();
  }
  
  if (downtime > 0 && (millis() - downtime) > 80){
    digitalWrite(ledPin, LOW);
    downtime = 0;
  }

}else{
  
  buttonState = digitalRead(buttonPin);
  if (buttonState == HIGH) {
    digitalWrite(ledPin, LOW);
  }
  else {
    digitalWrite(ledPin, HIGH);
  }
  
}
}
