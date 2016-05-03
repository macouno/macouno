
//The pin connected to the light
int inPin = 2;
int outPin = 13;
int dVal = 100;

int state = HIGH;
int buttonState;
int pressed = 0;

long time = 0;
long debounce = 100;

void setup() {
  // put your setup code here, to run once:
  pinMode(inPin, INPUT);
  pinMode(outPin, OUTPUT);
}
void loop()
{
  buttonState = digitalRead(inPin);

  // if the input just went from LOW and HIGH and we've waited long enough
  // to ignore any noise on the circuit, toggle the output pin and remember
  // the time
  if(buttonState == LOW && pressed == 0 && millis() - time > debounce){
    if(state == HIGH){
      state = LOW;
    }else{
      state = HIGH;
    }
    pressed = 1;
    time = millis();
    
  }else if(buttonState == HIGH && pressed == 1){
    pressed = 0;
  }
  

  digitalWrite(outPin, state);

}
