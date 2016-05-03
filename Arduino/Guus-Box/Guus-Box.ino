
//Pin Definitions
//The 74HC595 using a protocol called SPI (for more details http://www.arduino.cc/en/Tutorial/ShiftOut)
//Which has three pins
int data = 6; 
int clock = 8;
int latch = 7;

//Used for single LED manipulation
int ledState = 0;
const int ON = HIGH;
const int OFF = LOW;

//The pin connected to the lights
int inGreen = 2;
int inRed1 = 3;
int inRed2 = 4;
int inRed3 = 5;
int debounce = 100;

int stateGreen = HIGH; // If the light is on or not
int stateRed1 = HIGH;
int stateRed2 = HIGH;
int stateRed3 = HIGH;
int buttonGreen; // Button state readout
int buttonRed1;
int buttonRed2;
int buttonRed3;
int pressedGreen = 0; // Remember if the button was pressed
int pressedRed1 = 0;
int pressedRed2 = 0;
int pressedRed3 = 0;

long timeGreen = 0;
long timeRed1 = 0;
long timeRed2 = 0;
long timeRed3 = 0;
long debounceGreen = debounce;
long debounceRed1 = debounce;
long debounceRed2 = debounce;
long debounceRed3 = debounce;
/*
// THE PIEZO
int piezoPin = 9;
int piezoOn = 0;
int piezoState = LOW;
int piezoDuration = 1000;
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
*/
void setup() {
  // put your setup code here, to run once:
  pinMode(inGreen, INPUT);
  pinMode(outGreen, OUTPUT);
  pinMode(inRed1, INPUT);
  pinMode(outRed1, OUTPUT);
  pinMode(inRed2, INPUT);
  pinMode(outRed2, OUTPUT);
  pinMode(inRed3, INPUT);
  pinMode(outRed3, OUTPUT);

  //pinMode(piezoPin, OUTPUT);

  pinMode(data, OUTPUT);
  pinMode(clock, OUTPUT);  
  pinMode(latch, OUTPUT); 
}

void loop()
{

  /*
  if(piezoOn == 0){
    PlayTone(piezoTone, piezoDuration);
    piezoOn = 1;
  }*/
  
  buttonGreen = digitalRead(inGreen);
  buttonRed1 = digitalRead(inRed1);
  buttonRed2 = digitalRead(inRed2);
  buttonRed3 = digitalRead(inRed3);

  // if the input just went from LOW and HIGH and we've waited long enough
  // to ignore any noise on the circuit, toggle the output pin and remember
  // the time
  if(millis() - timeGreen > debounceGreen){
    if(buttonGreen == LOW && pressedGreen == 0){
      stateGreen = SwapState(0, stateGreen);
      stateRed1 = SwapState(1, stateRed1);
      stateRed2 = SwapState(2, stateRed2);
      stateRed3 = SwapState(3, stateRed3);
      pressedGreen = 1;
      timeGreen = millis();
      
    }else if(buttonGreen == HIGH && pressedGreen == 1){
      pressedGreen = 0;
      timeGreen = millis();
    }
  }  

  if(millis() - timeRed1 > debounceRed1){
    if(buttonRed1 == LOW && pressedRed1 == 0){
      stateRed1 = SwapState(1, stateRed1);
      pressedRed1 = 1;
      timeRed1 = millis();
      
    }else if(buttonRed1 == HIGH && pressedRed1 == 1){
      pressedRed1 = 0;
      timeRed1 = millis();
    }
  }
 
  if(millis() - timeRed2 > debounceRed2){
    if(buttonRed2 == LOW && pressedRed2 == 0){
      stateRed2 = SwapState(2, stateRed2);
      pressedRed2 = 1;
      timeRed2 = millis();
      
    }else if(buttonRed2 == HIGH && pressedRed2 == 1){
      pressedRed2 = 0;
      timeRed2 = millis();
    }
  }


  if(millis() - timeRed3 > debounceRed3){
    if(buttonRed3 == LOW && pressedRed3 == 0){
      stateRed3 = SwapState(3, stateRed3);
      pressedRed3 = 1;
      timeRed3 = millis();
      
    }else if(buttonRed3 == HIGH && pressedRed3 == 1){
      pressedRed3 = 0;
      timeRed3 = millis();
    }
  }

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

/*
 * updateLEDsLong() - sends the LED states set in ledStates to the 74HC595
 * sequence. Same as updateLEDs except the shifting out is done in software
 * so you can see what is happening.
 */ 
void updateLEDsLong(int value){
  digitalWrite(latch, LOW);    //Pulls the chips latch low
  for(int i = 0; i < 8; i++){  //Will repeat 8 times (once for each bit)
  int bit = value & B10000000; //We use a "bitmask" to select only the eighth 
                               //bit in our number (the one we are addressing this time through
  value = value << 1;          //we move our number up one bit value so next time bit 7 will be
                               //bit 8 and we will do our math on it
  if(bit == 128){digitalWrite(data, HIGH);} //if bit 8 is set then set our data pin high
  else{digitalWrite(data, LOW);}            //if bit 8 is unset then set the data pin low
  digitalWrite(clock, HIGH);                //the next three lines pulse the clock pin
  delay(1);
  digitalWrite(clock, LOW);
  }
  digitalWrite(latch, HIGH);  //pulls the latch high shifting our data into being displayed
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

