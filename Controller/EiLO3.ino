// Copyright (C) 2025 - 2026 Backdoor Interactive
// Externally Integrated Lights-Out 3 Arduino Controller Source
// Code tested with an Arduino Uno R3 (Genuine)

const int manPwrBtn = 2; // Manual power button connection
const int powerPin = 4; // Power header on motherboard --> arduino + ground
const int resetPin = 8;  // Reset header on motherboard --> arduino + ground
int incomingByte;        // a variable to read incoming serial data into

// ============================================================ The setup
// First wire the power button (Not the motherboard!) to Pin 2 and ground
// Then wire the power button header (On the motherboard!) to Pin 4 and ground
// [OPTIONAL] Wire the reset header to Pin 8 and ground for reset functionality

void setup() {
  // initialize EiLO Serial
  Serial.begin(9600);
  pinMode(powerPin, OUTPUT);
  pinMode(resetPin, OUTPUT);
  digitalWrite(powerPin, HIGH); // Change this depending on how your system reacts to the powerbutton intially | If its all wired correctly and the power button doesnt work, Try changing this to LOW
  digitalWrite(resetPin, LOW);
  pinMode (manPwrBtn, INPUT_PULLUP); // The manual power button is the actual power button so we can maintain control
}

int val = 0;  // Power button variable
void momentaryPress() {
      digitalWrite(powerPin, LOW); // Press
      delay(500);
      digitalWrite(powerPin, HIGH); // Release
}
void pressAndHold() {
      digitalWrite(powerPin, LOW);
      delay(5000); // Hold it for ~ 5 seconds
      digitalWrite(powerPin, HIGH); // Release
}
void resetMomentaryPress() {
      digitalWrite(resetPin, LOW);
      delay(500);
      digitalWrite(resetPin, HIGH);
}

void loop() {
  // EiLO Commands
  val = digitalRead(manPwrBtn);
  //Serial.println(val);
  digitalWrite(powerPin, val);  
    if (val == LOW){
        Serial.println("Status: Power Button Active");
    }
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == 'A') {
        Serial.println("Power: Momentary Press");
        momentaryPress();
    }
    if (incomingByte == 'B') {
        Serial.println("Power: Press And Hold");
        pressAndHold();
    }
    if (incomingByte == 'C') {
        Serial.println("Power: Reset Momentary Press");
        resetMomentaryPress();
    }
  }
}