int enB = 10;
int in3 = 12;
int in4 = 13;

const int buttonPin = 5;     // the number of the pushbutton pin
const int ledPin =  7;      // the number of the LED pin
const int switchPin =  6;      // the number of the LED pin

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status
int switchState = LOW;

void setup() {
  Serial.begin(19200);
  Serial.setTimeout(2);
  
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin,  INPUT_PULLUP);
  pinMode(switchPin,  INPUT_PULLUP);
  digitalWrite(ledPin, HIGH);
  delay(500);
  switchState = digitalRead(switchPin);
  
  pinMode(enB, OUTPUT);
  digitalWrite(enB, LOW);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
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
    }
  }
  
  long delta = (millis() - laststart)/10L;    
  if (switchState) {
    
    if (jump > 0 && downtime == 0) {
      digitalWrite(ledPin, LOW);
      digitalWrite(enB, HIGH);
      downtime = millis();
    }
    
    if (downtime > 0 && (millis() - downtime) > 80){
      digitalWrite(ledPin, HIGH);
      digitalWrite(enB, LOW);
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
