const int buttonPin = 2;     // the number of the pushbutton pin
const int ledPin =  4;      // the number of the LED pin
const int switchPin =  3;      // the number of the LED pin

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status
int switchState = LOW;

void setup() {
  Serial.begin(19200);
  Serial.setTimeout(2);
  
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin,  INPUT_PULLUP);
  pinMode(switchPin,  INPUT_PULLUP);
  digitalWrite(ledPin, LOW);
  delay(500);
  switchState = digitalRead(switchPin);
  
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  showTime(-1);
}

void showTime(long t){
  if (t >= 0){
    t = t % 25;
    digitalWrite(5, t & 0b00001);
    digitalWrite(6, t & 0b00010);
    digitalWrite(7, t & 0b00100);
    digitalWrite(8, t & 0b01000);
    digitalWrite(9, t & 0b10000);
  }else{
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
    digitalWrite(7, HIGH);
    digitalWrite(8, HIGH);
    digitalWrite(9, HIGH);
  }
}

unsigned long downtime = 0;
char buf[100];
unsigned long laststart = 0;

void loop() {
  int start_time = 0;
  int jump = 0;
  
  if (Serial.available() > 0) {
    int n = Serial.readBytes(buf, 100);
    for(int i=0;i<n;i++){
      if (buf[i] == '\n') {
        jump = 1;
      }
      else if (buf[i] == ' ') {
        laststart = millis();
      }
    }
  }
  
  long delta = (millis() - laststart)/10L;
  showTime(delta);
    
  if (switchState) {
    
    if (jump > 0 && downtime == 0) {
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
