int debug = 0;

//Pin Definitions
//The 74HC595 using a protocol called SPI (for more details http://www.arduino.cc/en/Tutorial/ShiftOut)
//Which has three pins
int data = 6; 
int clock = 8;
int latch = 7;


int firstLoop = 0;

//Used for single LED manipulation
unsigned long nTime = millis();
int ledState = 0;
const int ON = HIGH;
const int OFF = LOW;

//The pin connected to the lights
int cntLED = 6;
int inLED[] = {2,3,4,5,A0,A1};
int blinkLED[] = {0,0,0,0,500,500,1000,1000};
int debounceLED = 150;
int stateLED[] = {LOW, LOW, LOW, LOW, HIGH, LOW, HIGH, LOW};
int roundState = HIGH;
int stickState = HIGH;
int swapped = 1;
int buttonLED[5];
int pressedLED[] = {0,0,0,0,0,0,0,0};

long timeLED[] = {0,0,0,0,0,0,0,0};

// Extra LEDs
int enableBlink = 0;
int exOut[] = {11,12,13};
int exState[] = {HIGH,HIGH,HIGH};
int exGo[] = {0,0,0};
int exLen[] = {6,6,8};
int exTime[] = {0,0,0};
int exBlink[] = {500,250,250};

// THE PIEZO
int piezoPin = 9;
int piezoState = LOW;
int piezoDuration = 500;
int piezoTone = 1136;

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
  // Start the buttons
  for(int a = 0; a < 6; a++){
    pinMode(inLED[a], INPUT);
  }
  // Start the extra lights
  for(int a = 0; a < 3; a++){
    pinMode(exOut[a], OUTPUT);
  }

  pinMode(piezoPin, OUTPUT);

  pinMode(data, OUTPUT);
  pinMode(clock, OUTPUT);  
  pinMode(latch, OUTPUT); 

}

void loop()
{

  nTime = millis(); 

  // SET ALL LEDS TO WHAT THEY SHOULD BE
  if(swapped == 1){
    for(int b = 0; b < 8; b++){
      changeLED(b, stateLED[b]);
    }
    swapped = 0;
  }
  
  if(firstLoop == 0){
    
    for(int a = 0; a < 3; a++){
      digitalWrite(exOut[a], exState[a]);
    }

    stickState = digitalRead(inLED[4]);
    roundState = digitalRead(inLED[5]);

    PlayTone(piezoTone, piezoDuration);
    
    firstLoop = 1;
    
  }else{

    for(int i = 0; i < cntLED; i++){ 
      buttonLED[i] = digitalRead(inLED[i]);
    }
  
    for(int i = 0; i < cntLED; i++){
      
      if(i < 4){
        if((nTime - timeLED[i]) > debounceLED){
          if(buttonLED[i] == LOW && pressedLED[i] == 0){
  
            if(debug == 1){
              Serial.print("\n - pressed ");
              Serial.print(i);
            }
            pressedLED[i] = 1;
            timeLED[i] = nTime;
            swapped = 1;
            
            if(i == 0){
              for(int j = 0; j < 4; j++){
                stateLED[j] = SwapState(j, stateLED[j]);
              }
              break;
            }else{
              stateLED[i] = SwapState(i, stateLED[i]);

              // Start some blinking in certain cases
              if(i == 1 && exGo[2] == 0 && buttonLED[4] == HIGH && buttonLED[5] == HIGH){
                exGo[2] = 1;
                exTime[2] = nTime;
                //PlayTone(1136, 500);
              }else if(i == 2 && exGo[1] == 0 && buttonLED[4] == LOW && buttonLED[5] == LOW){
                exGo[1] = 1;
                exTime[1] = nTime;
              }else if(i == 3 && exGo[0] == 0 && buttonLED[4] == HIGH && buttonLED[5] == LOW){
                exGo[0] = 1;
                exTime[0] = nTime;
              }
              break;
            }
          }else if(buttonLED[i] == HIGH && pressedLED[i] == 1){
            
            pressedLED[i] = 0;
          }
          
        }
     
      // SWAP THE WHITE LIGHTS
      }else if(i == 4){
        int k = i + 1;
        if((buttonLED[i] == LOW && stateLED[i] == LOW) || (buttonLED[i] == HIGH && stateLED[i] == HIGH)){
          stateLED[i] = SwapState(i, stateLED[i]);
          stateLED[k] = SwapState(k, stateLED[k]);

          // If the round button is pressed then also swap them!
          if(buttonLED[5] == LOW){
            int l = i+2;
            int m = l+1;
            stateLED[l] = SwapState(l, stateLED[l]);
            stateLED[m] = SwapState(m, stateLED[m]);            
          }
          swapped = 1;
          break;
        }
      
      // SWAP THE BLUE AND ORANGE
      }else if(i == 5){
        int l = i+1;
        int m = l+1;
        if(buttonLED[i] != roundState){
          stateLED[l] = SwapState(l, stateLED[l]);
          stateLED[m] = SwapState(m, stateLED[m]);
          swapped = 1;  
          roundState = buttonLED[i];

          // Lets blink the string!
          if(buttonLED[4] == LOW && exGo[0] == 0){
            exGo[0]= 1;
            exTime[0] = nTime;
          }
          
          break;  
        }
      }
     
    }

    // Blinking lights
    if(enableBlink == 1){
      for(int a = 0; a < 3; a++){
        if(exGo[a] > 0){
          if((nTime - exTime[a]) > exBlink[a]){
            if(exState[a] == HIGH){
              exState[a] = LOW;
            }else{
              exState[a] = HIGH;
            }
            exTime[a] = nTime;
            exGo[a]++;
            digitalWrite(exOut[a], exState[a]);
          }
          if(exGo[a] >= exLen[a]){
             exGo[a] = 0;
             if(exState[a] == LOW){
               exState[a] = HIGH;
               digitalWrite(exOut[a], exState[a]);
             }
          }
        }
      }
    }
  }

  delay(100);
}

int SwapState(int led, int state){
  if(debug == 1){
    Serial.print(" - set ");
    Serial.print(led);
    Serial.print(" to ");
    Serial.print(state);
  }
  if(state == HIGH){
    //changeLED(led, 0);
    return LOW;
  }
  //changeLED(led, 1);
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

