#include <Servo.h>
Servo myServo; // create servo object to control a servo
int posServo = 0; // variable to store the servo position 

int debug = 1;

//Pin Definitions
//The 74HC595 using a protocol called SPI (for more details http://www.arduino.cc/en/Tutorial/ShiftOut)
//Which has three pins
int data = 6; 
int clock = 8;
int latch = 7;

int lop = 0;

//Used for single LED manipulation
unsigned long nTime = millis();
int ledState = 0;
const int ON = HIGH;
const int OFF = LOW;

//The pin connected to the lights
int cntLED = 4;
int inLED[] = {2,3,4,5,A0,A1};
int blinkLED[] = {0,0,0,0,500,1000};
int debounceLED = 100;
int stateLED[] = {LOW, LOW, LOW, LOW, LOW, LOW};
int buttonLED[5];
int pressedLED[] = {0,0,0,0,0,0};

int whiteLed[] = {A0,A1};
int whiteTime[] = {0,0};
int whiteBlink[] = {500, 1000};

long timeLED[] = {0,0,0,0,0,0};

// THE PIEZO
int piezoPin = 9;
int piezoOn = 0;
int piezoState = LOW;
int piezoDuration = 500;
int piezoTone = 1915;

// PLAY A NOTE ON THE PIEZO ELEMENT
void PlayTone(int tone, int duration){
  for(long i = 0; i < duration * 1000L; i += tone * 2){
    digitalWrite(piezoPin, HIGH);
    delayMicroseconds(tone);
    digitalWrite(piezoPin, LOW);
    delayMicroseconds(tone);
  }
}

void setup() {

  if(debug == 1){
    Serial.begin(9600);
  }
  
  // put your setup code here, to run once:
  for(int i = 0; i < 4; i++){
    pinMode(inLED[i], INPUT);
  }

  pinMode(piezoPin, OUTPUT);

  pinMode(data, OUTPUT);
  pinMode(clock, OUTPUT);  
  pinMode(latch, OUTPUT); 

  //myServo.attach(13); // attaches the servo on pin 9 to the servo object
}

void loop()
{

  nTime = millis(); 
  if(debug == 1){
    Serial.print(" -\n");       // prints a label
    Serial.print(lop);
    lop++;
  }

  for(int i = 0; i < cntLED; i++){
    
    buttonLED[i] = digitalRead(inLED[i]);
    if(debug == 1){
      Serial.print(" - ");
      Serial.print(buttonLED[i]);
      Serial.print("-");
      Serial.print(pressedLED[i]);
      Serial.print(" ntime ");
      Serial.print(nTime - timeLED[i]);
    }
    
    if((nTime - timeLED[i]) > debounceLED){
      if(buttonLED[i] == LOW && pressedLED[i] == 0){

        if(i == 0){
          for(int j = 0; j < 4; j++){
            stateLED[j] = SwapState(j, stateLED[j]);    
          }
        
          /*
          posServo += 45;
          if(posServo > 135){
            posServo = 45;
          }
          myServo.write(posServo); // tell servo to go to position in variable 'pos'
          delay(15); // waits 15ms for the servo to reach the position
          */
          pressedLED[i] = 1;
          timeLED[i] = millis();
          break;
        }else{

          if(debug == 1){
            Serial.print(" - swap ");
            Serial.print(i);
          }
          stateLED[i] = SwapState(i, stateLED[i]);
          pressedLED[i] = 1;
          timeLED[i] = millis();
          break;
        }
      }else if(buttonLED[i] == HIGH && pressedLED[i] == 1){
        
        pressedLED[i] = 0;
      }
      
    }
    
  }

  // BLINK THE WHITE LED
  for(int i = 4; i < 6; i++){
    if((nTime - timeLED[i]) > blinkLED[i]){
      stateLED[i] = SwapState(i, stateLED[i]);   
      timeLED[i] = nTime;
    }
  }
  
  if(piezoOn == 0){
    PlayTone(piezoTone, piezoDuration);
    piezoOn = 1;
  }

  delay(100);
}

int SwapState(int led, int state){
  if(state == HIGH){
    changeLED(led, 0);
    return LOW;
  }
  changeLED(led, 1);
  return HIGH;
}

/*
 * updateLEDs() - sends the LED states set in ledStates to the 74HC595
 * sequence
 */
void updateLEDs(int value){
  digitalWrite(latch, LOW);     //Pulls the chips latch low
  shiftOut(data, clock, MSBFIRST, value); //Shifts out the 8 bits to the shift register
  digitalWrite(latch, HIGH);   //Pulls the latch high displaying the data
}

//These are used in the bitwise math that we use to change individual LEDs
//For more details http://en.wikipedia.org/wiki/Bitwise_operation
int bits[] = {B00000001, B00000010, B00000100, B00001000, B00010000, B00100000, B01000000, B10000000};
int masks[] = {B11111110, B11111101, B11111011, B11110111, B11101111, B11011111, B10111111, B01111111};
/*
 * changeLED(int led, int state) - changes an individual LED 
 * LEDs are 0 to 7 and state is either 0 - OFF or 1 - ON
 */
 void changeLED(int led, int state){
   ledState = ledState & masks[led];  //clears ledState of the bit we are addressing
   if(state == ON){ledState = ledState | bits[led];} //if the bit is on we will add it to ledState
   updateLEDs(ledState);              //send the new LED state to the shift register
 }  

